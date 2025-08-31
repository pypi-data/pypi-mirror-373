import logging
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

import valkey.exceptions
from twisted.internet.defer import inlineCallbacks
from vortex.Payload import Payload

from peek_worker_service.peek_worker_task_state import TaskState
from peek_worker_service.peek_worker_tuples import PeekWorkerTaskArgsTuple
from peek_worker_service.peek_worker_tuples import PeekWorkerTaskResultTuple
from peek_worker_service.peek_worker_valkey_session import (
    PeekValkeySessionFactory,
)
from peek_worker_service.peek_worker_valkey_session import (
    convertAsyncioMethodToDeferred,
)

logger = logging.getLogger(__name__)


class PeekWorkerProcessQueue:
    def __init__(self, url: str = "valkey://localhost:6379/0"):
        self.url = url
        self._valkeySessionFactory: PeekValkeySessionFactory = None

        self.taskQueueKey = "task_queue"
        self.taskArgsKey = "task_args"
        self.resultQueueKey = "result_queue"
        self.pendingTasksKey = "pending_tasks"
        self._isAlive = True

    def serialise(self, tuple_) -> str:
        # noinspection PyProtectedMember
        return Payload(tuples=[tuple_])._toJson()

    # noinspection SpellCheckingInspection
    def deserialise(self, jsonStr: str):
        # noinspection PyProtectedMember
        return Payload()._fromJson(jsonStr).tuples[0]

    @property
    def isActive(self) -> bool:
        return self._isAlive and self._valkeySessionFactory is not None

    @inlineCallbacks
    def start(self):
        yield self._startAsync()

    @convertAsyncioMethodToDeferred
    async def _startAsync(self):
        self._valkeySessionFactory = PeekValkeySessionFactory(
            url=self.url, maxConnections=4
        )

    @inlineCallbacks
    def shutdown(self):
        self._isAlive = False
        if not self._valkeySessionFactory:
            return

        try:
            yield self._shutdownAsync()

        except Exception as e:
            logger.debug(f"Error closing Valkey session factory: {e}")

    @convertAsyncioMethodToDeferred
    async def _shutdownAsync(self):
        await self._valkeySessionFactory.disconnectAsync()

    @convertAsyncioMethodToDeferred
    async def waitForTask(
        self, workerId: str
    ) -> Tuple[Optional[Dict[str, Any]], PeekWorkerTaskArgsTuple]:
        logger.debug(f"entering waitForTask")

        async with self._valkeySessionFactory() as client:
            while self.isActive:
                # Use BRPOP to block for 5 seconds to allow graceful shutdown
                try:
                    result = await client.brpop(
                        [self.pendingTasksKey], timeout=5
                    )
                except valkey.exceptions.TimeoutError:
                    continue

                if not result:
                    continue

                # result is a tuple: (key, taskId)
                taskId = result[1]

                # Get task details
                taskKey = f"{self.taskQueueKey}:{taskId}"
                taskData = await client.get(taskKey)

                if not taskData:
                    logger.debug(f"task {taskId[:8]} not found")
                    continue

                task = self.deserialise(taskData)

                if task.get("status") != TaskState.PENDING.value:
                    logger.debug(f"task {taskId[:8]} no longer pending")
                    continue

                # Get task arguments from separate key
                taskArgsKey = f"{self.taskArgsKey}:{taskId}"
                taskArgsData = await client.get(taskArgsKey)

                if not taskArgsData:
                    logger.debug(f"task args {taskId[:8]} not found")
                    continue

                taskArgs = self.deserialise(taskArgsData)

                # Mark task as processing
                now = datetime.now(timezone.utc)
                task["status"] = TaskState.PROCESSING.value
                task["worker_id"] = workerId
                task["started_at"] = now.isoformat()
                task["dequeued_at"] = now.isoformat()

                taskSerialized = self.serialise(task)
                await client.set(taskKey, taskSerialized)

                logger.debug(f"successfully dequeued task {task['_id'][:8]}")
                return task, taskArgs

            return None, PeekWorkerTaskArgsTuple()

    @convertAsyncioMethodToDeferred
    async def queueResult(
        self, taskId: str, resultTuple: PeekWorkerTaskResultTuple
    ):
        logger.debug(
            f"Queuing result for task {taskId[:8]}, error: {resultTuple.error is not None}"
        )
        now = datetime.now(timezone.utc)

        # Update the result tuple with timing information
        resultTuple.taskId = taskId
        resultTuple.completedAt = now

        async with self._valkeySessionFactory() as client:
            # Get task info to populate timing fields and update final status
            taskKey = f"{self.taskQueueKey}:{taskId}"
            taskData = await client.get(taskKey)
            if taskData:

                def parseDateTime(dateStr):
                    return datetime.fromisoformat(dateStr) if dateStr else None

                task = self.deserialise(taskData)
                resultTuple.startedAt = parseDateTime(task.get("started_at"))
                resultTuple.dequeuedAt = parseDateTime(task.get("dequeued_at"))

                # Update task status
                task["status"] = (
                    TaskState.COMPLETED.value
                    if resultTuple.error is None
                    else TaskState.FAILED.value
                )
                task["finished_at"] = now.isoformat()
                taskSerialized = self.serialise(task)
                await client.set(taskKey, taskSerialized)

            # Push result to the single result queue using vortex serialization
            resultKey = self.resultQueueKey
            resultSerialized = self.serialise(resultTuple)
            await client.lpush(resultKey, resultSerialized)

            # Clean up task arguments since task is complete
            taskArgsKey = f"{self.taskArgsKey}:{taskId}"
            await client.delete(taskArgsKey)

    def close(self):
        self.shutdown()
