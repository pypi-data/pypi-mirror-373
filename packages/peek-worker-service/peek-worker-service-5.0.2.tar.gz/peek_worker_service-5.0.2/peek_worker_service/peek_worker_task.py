import logging
import uuid
from datetime import datetime
from datetime import timezone
from typing import Callable
from typing import Dict
from typing import Optional

from twisted.internet import reactor
from twisted.internet.defer import Deferred

from peek_worker_service.peek_worker_request_queue import PeekWorkerRequestQueue
from peek_worker_service.peek_worker_task_state import TaskState
from peek_worker_service.peek_worker_tuples import PeekWorkerTaskArgsTuple
from peek_worker_service.peek_worker_tuples import PeekWorkerTaskStartTuple


# Global task registry
_taskRegistry: Dict[str, "PeekWorkerTask"] = {}

logger = logging.getLogger(__name__)


class PeekWorkerTask:
    def __init__(self, retries: int, func: Callable):
        self.retries = retries
        self.func = func
        self.funcName = f"{func.__module__}.{func.__name__}"
        self.taskRequestManager: Optional[PeekWorkerRequestQueue] = None
        self._twistedRunning = True

        # Register the function in the global registry
        _taskRegistry[self.funcName] = self

        assert retries >= 0, "retries needs to be greater or equal to 0"

        def setStopped():
            self._twistedRunning = False

        reactor.addSystemEventTrigger("before", "shutdown", setStopped)

    def delay(self, *args, timeout: float = 1800.0, **kwargs):
        if not self._twistedRunning:
            logger.debug(
                "Not starting task %s, Reactor is stopping", self.funcName
            )

            # Return a deferred that won't fire.
            return Deferred()

        if self.taskRequestManager is None:
            raise RuntimeError(
                f"Task method {self.funcName} not initialized with taskRequestManager. "
                "Call initializeTaskMethod() first."
            )

        taskArgs = PeekWorkerTaskArgsTuple()
        taskArgs.taskMethod = self.funcName
        taskArgs.args = list(args)
        taskArgs.kwargs = kwargs

        requestArgs = PeekWorkerTaskStartTuple()
        requestArgs.taskId = str(uuid.uuid4())
        requestArgs.status = TaskState.PENDING.value
        now = datetime.now(timezone.utc)
        requestArgs.createdAt = now
        requestArgs.queuedAt = now
        requestArgs.workerId = None
        requestArgs.startedAt = None
        requestArgs.dequeuedAt = None
        requestArgs.finishedAt = None
        requestArgs.cancelledAt = None
        requestArgs.cancellationReason = None
        return self.taskRequestManager.queueTask(
            self.funcName, requestArgs, taskArgs, timeout
        )

    def __call__(self, *args, **kwargs):
        for retriesLeft in reversed(range(self.retries + 1)):
            try:
                return self.func(*args, **kwargs)
            except Exception as e:
                if not retriesLeft:
                    raise

                logger.warning(
                    "Task %s failed, retrying %s more times, %s",
                    self.funcName,
                    retriesLeft,
                    str(e),
                )

        raise Exception("This should never happen")

    def initializeTaskMethod(self, taskRequestManager: PeekWorkerRequestQueue):
        self.taskRequestManager = taskRequestManager
        return self


def peekWorkerTaskDecorator(retries: int):
    def wrapper(func: Callable) -> PeekWorkerTask:
        return PeekWorkerTask(retries, func)

    return wrapper


def initializeAllTaskMethods(
    taskRequestManager: PeekWorkerRequestQueue,
) -> Dict[str, PeekWorkerTask]:
    for funcName, func in _taskRegistry.items():
        func.initializeTaskMethod(taskRequestManager)

    return _taskRegistry
