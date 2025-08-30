from datetime import datetime
from typing import Any
from typing import Optional

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@addTupleType
class PeekWorkerTaskArgsTuple(Tuple):
    __tupleType__ = "PeekWorkerTaskArgsTuple"
    taskMethod: str = TupleField()
    args: list = TupleField()
    kwargs: dict = TupleField()


@addTupleType
class PeekWorkerTaskStartTuple(Tuple):
    __tupleType__ = "PeekWorkerTaskStartTuple"
    taskId: str = TupleField()
    status: str = TupleField()
    createdAt: datetime = TupleField()
    queuedAt: datetime = TupleField()
    workerId: str = TupleField()
    startedAt: datetime = TupleField()
    dequeuedAt: datetime = TupleField()
    finishedAt: datetime = TupleField()
    cancelledAt: datetime = TupleField()
    cancellationReason: str = TupleField()


@addTupleType
class PeekWorkerTaskResultTuple(Tuple):
    __tupleType__ = "PeekWorkerTaskResultTuple"
    taskId: str = TupleField()
    result: Any = TupleField()
    error: Optional[str] = TupleField()
    completedAt: datetime = TupleField()
    startedAt: Optional[datetime] = TupleField()
    finishedAt: Optional[datetime] = TupleField()
    dequeuedAt: Optional[datetime] = TupleField()
    cancelledAt: Optional[datetime] = TupleField()
    cancellationReason: Optional[str] = TupleField()
