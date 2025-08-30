import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Dict

from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload

from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger
from peek_worker_service.peek_worker_task_state import TaskState
from peek_worker_service.peek_worker_tuples import PeekWorkerTaskArgsTuple
from peek_worker_service.peek_worker_tuples import PeekWorkerTaskResultTuple
from peek_worker_service.peek_worker_tuples import PeekWorkerTaskStartTuple
from peek_worker_service.peek_worker_valkey_session import (
    PeekValkeySessionFactory,
)
from peek_worker_service.peek_worker_valkey_session import (
    convertAsyncioMethodToDeferred,
)

logger = logging.getLogger(__name__)


class PeekWorkerRequestQueue:
    LOOPING_CALL_PERIOD = 3600  # 1 hour in seconds
    MONITORING_PERIOD = 300  # 5 minutes in seconds
    MAX_CONCURRENT_TASK_REQUEST_CONNECTIONS = 10
    MAX_CONCURRENT_TASK_RESULT_CONNECTIONS = 2

    def __init__(self, url: str = "valkey://localhost:6379/0"):
        self.url = url

        self._poolRequestSemphore = defer.DeferredSemaphore(
            tokens=self.MAX_CONCURRENT_TASK_REQUEST_CONNECTIONS
        )

        self._valkeySessionCreator: PeekValkeySessionFactory = None

        self.taskQueueKey = "task_queue"
        self.taskArgsKey = "task_args"
        self.resultQueueKey = "result_queue"
        self.taskTimingKey = "task_timing"
        self.pendingTasksKey = "pending_tasks"
        self._isAlive = False
        self._runningTasksByTaskId: Dict[str, "PeekTaskResult"] = {}
        self._loopRunning = False

        # Initialize looping calls
        self._cleanupLoopingCall = LoopingCall(
            peekCatchErrbackWithLogger(logger)(self._removeOldTasksWrapper)
        )
        self._monitoringLoopingCall = LoopingCall(
            peekCatchErrbackWithLogger(logger)(self._monitorValkeyStatus)
        )

    def serialise(self, tuple_) -> str:
        # noinspection PyProtectedMember
        return Payload(tuples=[tuple_])._toJson()

    # noinspection SpellCheckingInspection
    def deserialise(self, jsonStr: str):
        # noinspection PyProtectedMember
        return Payload()._fromJson(jsonStr).tuples[0]

    # noinspection SpellCheckingInspection
    @deferToThreadWrapWithLogger(logger)
    def deserialiseInThread(self, jsonStr: str):
        return self.deserialise(jsonStr)

    @property
    def isActive(self) -> bool:
        return self._isAlive and self._valkeySessionCreator is not None

    @convertAsyncioMethodToDeferred
    async def start(self):
        self._isAlive = True
        self._valkeySessionCreator = PeekValkeySessionFactory(
            url=self.url,
            maxConnections=(
                self.MAX_CONCURRENT_TASK_RESULT_CONNECTIONS
                + self.MAX_CONCURRENT_TASK_REQUEST_CONNECTIONS
                + 10  # Add some buffer
            ),
        )

        # Test connection
        async with self._valkeySessionCreator() as client:
            await client.ping()
            logger.info(f"Successfully connected to Valkey at {self.url}")

        # Clear queues on startup
        await self._cleanupCollectionsAsync()

        # Start looping calls
        d1 = self._cleanupLoopingCall.start(self.LOOPING_CALL_PERIOD, now=True)
        d1.addErrback(vortexLogFailure, logger, consumeError=True)

        d2 = self._monitoringLoopingCall.start(self.MONITORING_PERIOD, now=True)
        d2.addErrback(vortexLogFailure, logger, consumeError=True)

    def shutdown(self):
        self._isAlive = False

        if self._cleanupLoopingCall is not None:
            self._cleanupLoopingCall.stop()
            self._cleanupLoopingCall = None

        if self._monitoringLoopingCall is not None:
            self._monitoringLoopingCall.stop()
            self._monitoringLoopingCall = None

    @convertAsyncioMethodToDeferred
    async def _monitorValkeyStatus(self):
        if not self._valkeySessionCreator:
            return

        try:
            async with self._valkeySessionCreator() as client:
                info = await client.info()

                # Log interesting connection and memory stats
                connectedClients = info.get("connected_clients", "N/A")
                usedMemory = info.get("used_memory_human", "N/A")
                totalConnectionsReceived = info.get(
                    "total_connections_received", "N/A"
                )
                totalCommandsProcessed = info.get(
                    "total_commands_processed", "N/A"
                )
                keyspaceHits = info.get("keyspace_hits", "N/A")
                keyspaceMisses = info.get("keyspace_misses", "N/A")

                logger.info(
                    f"Valkey Status - Connected clients: {connectedClients}, "
                    f"Memory used: {usedMemory}, "
                    f"Total connections: {totalConnectionsReceived}, "
                    f"Commands processed: {totalCommandsProcessed}, "
                    f"Keyspace hits: {keyspaceHits}, misses: {keyspaceMisses}"
                )

                # Log pool stats - use async pool properties
                inUseConnections = self._valkeySessionCreator.inUseConnections
                waitingConnections = max(
                    0,
                    inUseConnections
                    - self._valkeySessionCreator.maxConnections,
                )
                logger.info(
                    f"Connection Pool - Max: "
                    f"{self._valkeySessionCreator.maxConnections}, "
                    f"Created: {self._valkeySessionCreator.createdConnections}, "
                    f"Available: {self._valkeySessionCreator.availableConnections}, "
                    f"In Use: {inUseConnections}, "
                    f"Waiting: {waitingConnections}"
                )

        except Exception as e:
            logger.error(f"Error monitoring Valkey status: {e}")

    def queueTask(
        self,
        taskMethod: str,
        requestArgs: PeekWorkerTaskStartTuple,
        taskArgs: PeekWorkerTaskArgsTuple,
        timeout: float,
    ) -> "TaskResult":
        from peek_worker_service.peek_worker_task_result import PeekTaskResult

        taskId = requestArgs.taskId
        taskResult = PeekTaskResult(self, taskId, timeout)

        # Store the task result in running tasks
        self._runningTasksByTaskId[taskId] = taskResult

        # Queue the task
        queueD = self._poolRequestSemphore.run(
            self._queueTask, taskMethod, requestArgs, taskArgs
        )
        queueD.addErrback(
            lambda f: logger.error(f"Error queueing task: {f.value}")
        )
        reactor.callLater(0, self._resultLoopSingleton)

        return taskResult

    @convertAsyncioMethodToDeferred
    async def _queueTask(
        self,
        taskMethod: str,
        requestArgs: PeekWorkerTaskStartTuple,
        taskArgs: PeekWorkerTaskArgsTuple,
    ):
        taskId = requestArgs.taskId
        logger.debug(f"Queuing task {taskId[:8]} ({taskMethod})")

        async with self._valkeySessionCreator() as client:
            # Store task arguments separately
            taskArgsKey = f"{self.taskArgsKey}:{taskId}"
            serializedArgs = self.serialise(taskArgs)
            await client.set(taskArgsKey, serializedArgs)

            # Store task metadata without arguments
            taskDoc = {
                "_id": taskId,
                "status": requestArgs.status,
                "created_at": requestArgs.createdAt.isoformat(),
                "queued_at": (
                    requestArgs.queuedAt.isoformat()
                    if requestArgs.queuedAt
                    else None
                ),
                "worker_id": requestArgs.workerId,
                "started_at": (
                    requestArgs.startedAt.isoformat()
                    if requestArgs.startedAt
                    else None
                ),
                "dequeued_at": (
                    requestArgs.dequeuedAt.isoformat()
                    if requestArgs.dequeuedAt
                    else None
                ),
                "finished_at": (
                    requestArgs.finishedAt.isoformat()
                    if requestArgs.finishedAt
                    else None
                ),
                "cancelled_at": (
                    requestArgs.cancelledAt.isoformat()
                    if requestArgs.cancelledAt
                    else None
                ),
                "cancellation_reason": requestArgs.cancellationReason,
            }

            # Store task data using vortex serialization
            taskKey = f"{self.taskQueueKey}:{taskId}"
            taskDocSerialized = self.serialise(taskDoc)
            await client.set(taskKey, taskDocSerialized)

            # Add to pending tasks list for workers to block on
            await client.lpush(self.pendingTasksKey, taskId)

        logger.debug(f"Task {taskId[:8]} successfully queued")

    def _resultLoopSingleton(self):
        """Singleton wrapper for the result loop"""
        if self._loopRunning:
            return

        if not self._runningTasksByTaskId:
            return

        def setNotRunning(*args):
            self._loopRunning = False

        self._loopRunning = True
        d = self._resultLoop()
        d.addErrback(lambda f: logger.error(f"Error in result loop: {f.value}"))
        d.addBoth(setNotRunning)

    @convertAsyncioMethodToDeferred
    async def _resultLoop(self):
        """Combined result loop method"""

        async with self._valkeySessionCreator() as client:
            while self.isActive and self._runningTasksByTaskId:
                # Check for timed out tasks
                timedOutTasks = []
                for taskId, taskResult in self._runningTasksByTaskId.items():
                    if taskResult.hasTimedOut:
                        timedOutTasks.append(taskId)

                # Handle timed out tasks
                for taskId in timedOutTasks:
                    logger.info(f"Task {taskId[:8]} timed out")
                    taskResult = self._runningTasksByTaskId.pop(taskId)
                    await self._markTaskAsCancelledAsync(
                        taskId,
                        f"Timeout waiting for result after {taskResult._timeout}s",
                    )
                    taskResult.errback(
                        TimeoutError(
                            f"Timeout waiting for result after {taskResult._timeout}s"
                        )
                    )

                if not self._runningTasksByTaskId:
                    return

                while True:
                    result = await client.blpop(self.resultQueueKey, timeout=5)
                    if not result:
                        break

                    reactor.callLater(0, self._handleResult, result)

    @inlineCallbacks
    def _handleResult(self, result):
        """Handle a result from the queue"""
        assert result, "_handleResult: Result must not be None"

        # Deserialize result
        resultTuple = yield self.deserialiseInThread(result[1])
        taskId = resultTuple.taskId

        # Get the running task
        if taskId not in self._runningTasksByTaskId:
            logger.warning(f"Received result for unknown task {taskId[:8]}")
            return

        taskResult = self._runningTasksByTaskId.pop(taskId)

        if resultTuple.startedAt:
            took = datetime.now(timezone.utc) - resultTuple.startedAt
        else:
            took = "[startedAt is None]"

        logger.info(f"Task {taskId[:8]} result received, took {took}")

        # Resolve the deferred
        if taskResult.called:
            logger.debug(f"Task {taskId[:8]} deferred already called")
        elif resultTuple.error:
            taskResult.errback(Exception(resultTuple.error))
        else:
            taskResult.callback(resultTuple.result)

    async def _markTaskAsCancelledAsync(self, taskId: str, reason: str = None):
        now = datetime.now(timezone.utc)

        async with self._valkeySessionCreator() as client:
            assert taskId in self._runningTasksByTaskId, (
                "Can not cancel task %s, it is not in the running tasks"
                % taskId
            )
            taskResult = self._runningTasksByTaskId.pop(taskId)

            assert not taskResult.called, (
                "The taskResult for task %s has already been called" % taskId
            )
            taskResult.errback(
                Exception(
                    f"Task cancelled: {reason}" if reason else "Task cancelled"
                )
            )

            # Update task status
            taskKey = f"{self.taskQueueKey}:{taskId}"
            taskData = await client.get(taskKey)
            if taskData:
                task = self.deserialise(taskData)
                task["status"] = TaskState.CANCELLED.value
                task["cancelled_at"] = now.isoformat()
                task["cancellation_reason"] = reason

                taskSerialized = self.serialise(task)
                await client.set(taskKey, taskSerialized)

            # Queue cancellation result using vortex serialization
            # We queue this, so that any blocking waits will also wake up.
            error = f"Task cancelled: {reason}" if reason else "Task cancelled"
            resultTuple = PeekWorkerTaskResultTuple()
            resultTuple.taskId = taskId
            resultTuple.result = None
            resultTuple.error = error
            resultTuple.completedAt = now
            resultTuple.startedAt = None
            resultTuple.finishedAt = None
            resultTuple.dequeuedAt = None
            resultTuple.cancelledAt = now
            resultTuple.cancellationReason = reason
            resultSerialized = self.serialise(resultTuple)
            await client.lpush(self.resultQueueKey, resultSerialized)

    @convertAsyncioMethodToDeferred
    async def _removeOldTasksWrapper(self):
        oneHourAgo = datetime.now(timezone.utc) - timedelta(hours=1)

        async with self._valkeySessionCreator() as client:
            taskKeys = await client.keys(f"{self.taskQueueKey}:*")
            keysToDelete = []

            for taskKey in taskKeys:
                taskData = await client.get(taskKey)
                if not taskData:
                    continue

                task = self.deserialise(taskData)
                dequeuedAtStr = task.get("dequeued_at")

                if not dequeuedAtStr:
                    continue

                dequeuedAt = datetime.fromisoformat(dequeuedAtStr)
                if dequeuedAt < oneHourAgo:
                    taskId = task["_id"]
                    keysToDelete.extend(
                        [taskKey, f"{self.taskArgsKey}:{taskId}"]
                    )

            if keysToDelete:
                await client.delete(*keysToDelete)
                await client.delete(*keysToDelete)
                logger.info(f"Removed {len(keysToDelete)} old task keys")

    async def _cleanupCollectionsAsync(self):
        async with self._valkeySessionCreator() as client:
            # Get all keys matching our patterns
            taskKeys = await client.keys(f"{self.taskQueueKey}:*")
            taskArgsKeys = await client.keys(f"{self.taskArgsKey}:*")

            # Delete all task, task args keys and the single result queue
            allKeys = (
                taskKeys
                + taskArgsKeys
                + [self.pendingTasksKey, self.resultQueueKey]
            )
            if allKeys:
                await client.delete(*allKeys)

    def close(self):
        self.shutdown()
        if self._valkeySessionCreator:
            try:
                # Use aclose() for async connection pool
                defer.ensureDeferred(
                    self._valkeySessionCreator.disconnectAsync()
                )
            except Exception as e:
                logger.debug(f"Error disconnecting connection pool: {e}")
