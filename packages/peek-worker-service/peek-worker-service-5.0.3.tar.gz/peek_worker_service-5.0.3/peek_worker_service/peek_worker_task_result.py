from datetime import datetime
from datetime import timezone
from typing import Any
from typing import NamedTuple
from typing import Optional

from twisted.internet import defer

from peek_worker_service.peek_worker_request_queue import PeekWorkerRequestQueue


class _PeekTaskResultTuple(NamedTuple):
    success: bool
    result: Optional[Any]
    error: Optional[str]
    timeoutError: Optional[bool] = False


class PeekTaskResult(defer.Deferred):
    def __init__(
        self,
        taskRequestManager: PeekWorkerRequestQueue,
        taskId: str,
        timeout: float,
    ):
        defer.Deferred.__init__(self)
        self.taskRequestManager = taskRequestManager
        self._taskId = taskId
        self._timeout = timeout
        self._startTime = datetime.now(timezone.utc)

    @property
    def taskId(self) -> str:
        return self._taskId

    @property
    def hasTimedOut(self) -> bool:
        elapsed = (datetime.now(timezone.utc) - self._startTime).total_seconds()
        return elapsed >= self._timeout
