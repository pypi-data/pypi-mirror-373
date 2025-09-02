from twisted.internet import asyncioreactor
from twisted.internet.error import ReactorAlreadyInstalledError

try:
    # CRITICAL: Install asyncioreactor BEFORE importing any other twisted modules
    asyncioreactor.install()
except ReactorAlreadyInstalledError:
    # This is a subprocess, so this is expected. Continue running.
    pass

import logging
import os
import signal
import sys
import uuid
from datetime import datetime
from datetime import timezone
from importlib.util import find_spec
from typing import Optional

from setproctitle import setproctitle
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from vortex import Tuple as TupleMod
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_platform.util.LogUtil import setupPeekLogger
from peek_plugin_base.PeekVortexUtil import peekWorkerName
from peek_worker_service.peek_worker_task import PeekWorkerTask

# This is a subprocess, so __main__ doensn't work
logger = logging.getLogger("peek_plugin_worker.peek_worker_process")


class PeekWorkerProcess:
    def __init__(
        self,
        TUPLE_TYPES,
        TUPLE_TYPES_BY_NAME,
        TUPLE_TYPES_BY_SHORT_NAME,
        url: str,
        enabledPlugins: list[str],
    ):
        from peek_worker_service.peek_worker_process_queue import (
            PeekWorkerProcessQueue,
        )

        self._TUPLE_TYPES = TUPLE_TYPES
        self._TUPLE_TYPES_BY_NAME = TUPLE_TYPES_BY_NAME
        self._TUPLE_TYPES_BY_SHORT_NAME = TUPLE_TYPES_BY_SHORT_NAME

        self.workerId: str = str(uuid.uuid4())[:8]
        self.url = url
        self.processId: Optional[int] = None
        self.workerQueue: Optional["PeekWorkerProcessQueue"] = None
        self.running: bool = False
        self.shutdownRequested: bool = False
        self._tasksProcessed: int = 0

        self._enabledPluginsSet = set(enabledPlugins)

    @property
    def totalTasksProcessed(self) -> int:
        return self._tasksProcessed

    @property
    def isAlive(self) -> bool:
        return (
            self.running
            and not self.shutdownRequested
            and self.workerQueue
            and self.workerQueue.isActive
        )

    def start(self):
        """Start

        This is called by the subprocess
        """
        self.running = True
        self.processId = os.getpid()
        signal.signal(signal.SIGTERM, self.multiProcessShutdown)
        signal.signal(signal.SIGINT, self.multiProcessShutdown)

        TupleMod.TUPLE_TYPES = self._TUPLE_TYPES
        TupleMod.TUPLE_TYPES_BY_NAME = self._TUPLE_TYPES_BY_NAME
        TupleMod.TUPLE_TYPES_BY_SHORT_NAME = self._TUPLE_TYPES_BY_SHORT_NAME

        logger.info(f"started (PID: {self.processId})")
        setupPeekLogger(peekWorkerName, self.workerId, logToStdout=False)
        setproctitle(f"{peekWorkerName} {self.workerId}")

        logger.debug(f"starting reactor")
        # noinspection PyUnresolvedReferences
        reactor.callLater(0, self._startInReactor)
        # noinspection PyUnresolvedReferences
        reactor.run()

    def multiProcessShutdown(self, signum: int, frame):
        logger.info(
            f"received signal {signum}," f" initiating graceful shutdown"
        )
        self.shutdownRequested = True
        self.running = False

        # noinspection PyUnresolvedReferences
        reactor.callFromThread(self._shutdownInReactor)

    @inlineCallbacks
    def _startInReactor(self):

        from peek_worker_service.peek_worker_process_queue import (
            PeekWorkerProcessQueue,
        )

        self.workerQueue = PeekWorkerProcessQueue(self.url)
        yield self.workerQueue.start()

        # noinspection PyUnresolvedReferences
        reactor.callLater(0, self._checkAndProcessLoop)

    @inlineCallbacks
    def _shutdownInReactor(self):
        logger.info(f"shutting down gracefully")

        try:
            if self.workerQueue:
                yield self.workerQueue.shutdown()
        except Exception as e:
            logger.error(f"error closing worker queue: {e}")

        # noinspection PyUnresolvedReferences
        if reactor.running:
            # noinspection PyUnresolvedReferences
            reactor.stop()

    @inlineCallbacks
    def _checkAndProcessLoop(self):
        nextTaskDeferred = None
        while self.isAlive:

            try:
                if nextTaskDeferred:
                    taskDoc, taskArgs = yield nextTaskDeferred
                    nextTaskDeferred = None
                else:
                    result = yield self.workerQueue.waitForTask(self.workerId)
                    if not result:
                        continue
                    taskDoc, taskArgs = result

                if not taskDoc:
                    if self.shutdownRequested:
                        logger.info(f"exiting due to shutdown request")
                        break
                    logger.debug(f"waitForTask got None")
                    continue

                from peek_worker_service.peek_worker_task_state import TaskState

                if taskDoc.get("status") == TaskState.CANCELLED.value:
                    logger.info(f"skipped cancelled task {taskDoc['_id'][:8]}")
                    continue

                # Only prefetch next task if not shutting down
                if not self.shutdownRequested:
                    nextTaskDeferred = self.workerQueue.waitForTask(
                        self.workerId
                    )

                yield self._processTask(taskDoc, taskArgs)

            except Exception as e:
                logger.error(f"error in task loop: {e}")

            if not self.isAlive:
                logger.debug(f"exiting task loop")
                break

        logger.debug(f"task processing loop completed")

    @inlineCallbacks
    def _processTask(self, taskDoc: dict, taskArgs):
        taskId: str = taskDoc["_id"]
        taskMethodName: str = taskArgs.taskMethod
        args: list = taskArgs.args
        kwargs: dict = taskArgs.kwargs

        startTime = datetime.now(timezone.utc)

        logger.info(f"started task {taskId[:8]} ({taskMethodName})")

        from peek_worker_service.peek_worker_tuples import (
            PeekWorkerTaskResultTuple,
        )

        resultTuple = PeekWorkerTaskResultTuple()
        resultTuple.taskId = taskId
        resultTuple.completedAt = None
        resultTuple.startedAt = None
        resultTuple.finishedAt = None
        resultTuple.dequeuedAt = None
        resultTuple.cancelledAt = None
        resultTuple.cancellationReason = None

        try:
            pluginName = taskMethodName.split(".")[0]
            if (
                not pluginName.startswith("peek_core")
                and pluginName not in self._enabledPluginsSet
            ):
                raise Exception(
                    f"taskMethodWrapper '{taskMethodName}' is for a plugin"
                    f" not enabled in config.json"
                )

            result = yield self._runTaskMethod(taskMethodName, args, kwargs)

            resultTuple.result = result
            resultTuple.error = None
            yield self.workerQueue.queueResult(taskId, resultTuple)
            logger.info(
                f"completed task {taskId[:8]},"
                f" in {datetime.now(timezone.utc) - startTime}"
            )
            self._tasksProcessed = self._tasksProcessed + 1

        except Exception as e:
            errorMsg = str(e)
            logger.exception(f"failed task {taskId[:8]}: {errorMsg}")

            resultTuple.result = None
            resultTuple.error = errorMsg
            yield self.workerQueue.queueResult(taskId, resultTuple)

    @deferToThreadWrapWithLogger(logger)
    def _runTaskMethod(self, taskMethodName: str, args, kwargs):

        taskMethodWrapper = self._loadTaskMethodBlocking(taskMethodName)
        return taskMethodWrapper(*args, **kwargs)

    def _loadTaskMethodBlocking(self, taskMethodName: str) -> PeekWorkerTask:

        modName, functionName = taskMethodName.rsplit(".", 1)

        if modName in sys.modules:
            module = sys.modules[modName]
        else:
            modSpec = find_spec(modName)
            if not modSpec:
                raise Exception(
                    f"Failed to find module {modName}, is the python package installed?"
                )
            module = modSpec.loader.load_module()

        taskMethodWrapper = getattr(module, functionName)

        assert isinstance(taskMethodWrapper, PeekWorkerTask), (
            "taskMethodWrapper %s is not a PeekWorkerTask" % taskMethodName
        )
        return taskMethodWrapper
