import logging
import multiprocessing
import random
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import psutil
from valkey import ValkeyError
from vortex.Tuple import TUPLE_TYPES
from vortex.Tuple import TUPLE_TYPES_BY_NAME
from vortex.Tuple import TUPLE_TYPES_BY_SHORT_NAME

from peek_worker_service.peek_worker_process import PeekWorkerProcess
from peek_worker_service.peek_worker_valkey_session import (
    PeekValkeySessionFactory,
)
from peek_worker_service.peek_worker_valkey_session import (
    convertAsyncioMethodToDeferred,
)

logger = logging.getLogger(__name__)


class WorkerConfig(NamedTuple):
    url: str
    numWorkers: int
    maxWorkerTasksCompleted: int
    maxWorkerAgeSeconds: int
    maxMemoryMb: int
    enabledPlugins: list[str]


class WorkerState:
    def __init__(
        self, process: multiprocessing.Process, worker: PeekWorkerProcess
    ):
        self.process = process
        self.worker = worker
        self.startTime = datetime.now(timezone.utc)

    @property
    def workerAgeSeconds(self) -> float:
        return (datetime.now(timezone.utc) - self.startTime).total_seconds()

    @property
    def workerMemoryMb(self) -> int:
        processInfo = psutil.Process(self.process.pid)
        return int(processInfo.memory_info().rss / 1024 / 1024)

    def shouldRecycle(self, config: WorkerConfig) -> bool:
        if not self.process.is_alive():
            return True

        if self.worker.totalTasksProcessed > (
            config.maxWorkerTasksCompleted * random.uniform(0.9, 1.1)
        ):
            return True

        if self.workerAgeSeconds > (
            config.maxWorkerAgeSeconds * random.uniform(0.9, 1.1)
        ):
            return True

        try:
            processInfo = psutil.Process(self.process.pid)
            memoryMb = processInfo.memory_info().rss / 1024 / 1024
            if memoryMb > config.maxMemoryMb:
                return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return True

        return False


class PeekWorkerManager:
    def __init__(self, config: WorkerConfig):
        # Set multiprocessing start method to spawn on Linux
        try:
            multiprocessing.set_start_method("spawn", force=True)
        except RuntimeError:
            # Start method already set, continue
            pass

        self.config = config
        self._workers: Dict[str, WorkerState] = {}
        self._isRunning = False
        self._shutdownRequested = False
        self._valkeySessionFactory: Optional[PeekValkeySessionFactory] = None

    async def _connectToValkeyAsync(self):
        self._valkeySessionFactory = PeekValkeySessionFactory(
            url=self.config.url, maxConnections=2
        )
        # Test connection - will raise exception if connection fails
        async with self._valkeySessionFactory() as client:
            await client.ping()
            logger.info(f"Connected to Valkey at {self.config.url}")

    async def _disconnectFromValkeyAsync(self):
        if not self._valkeySessionFactory:
            return

        await self._valkeySessionFactory.disconnectAsync()
        self._valkeySessionFactory = None
        logger.info("Disconnected from Valkey")

    async def _pingValkeyAsync(self):
        if not self._valkeySessionFactory:
            return

        try:
            async with self._valkeySessionFactory() as client:
                await client.ping()
        except ValkeyError as e:
            logger.exception(f"Valkey ping failed: {e}")

    def _createWorker(self) -> WorkerState:
        worker = PeekWorkerProcess(
            TUPLE_TYPES=TUPLE_TYPES.copy(),
            TUPLE_TYPES_BY_NAME=TUPLE_TYPES_BY_NAME.copy(),
            TUPLE_TYPES_BY_SHORT_NAME=TUPLE_TYPES_BY_SHORT_NAME.copy(),
            url=self.config.url,
            enabledPlugins=self.config.enabledPlugins,
        )
        process = multiprocessing.Process(target=worker.start)
        process.start()
        return WorkerState(process, worker)

    def _recycleWorkers(self):
        if self._shutdownRequested:
            return

        workersToRecycle = []

        for workerId, workerState in self._workers.items():
            if workerState.shouldRecycle(self.config):
                workersToRecycle.append(workerId)

        for workerId in workersToRecycle:
            logger.info(f"Recycling worker {workerId}")
            self._stopWorker(workerId)

    async def _maintainWorkerCountAsync(self):
        if self._shutdownRequested:
            return

        self._recycleWorkers()
        await self._pingValkeyAsync()

        while (
            len(self._workers) < self.config.numWorkers
            and not self._shutdownRequested
        ):
            workerState = self._createWorker()
            workerId = f"worker_{workerState.process.pid}"
            self._workers[workerId] = workerState
            logger.info(
                f"Started worker {workerId} (PID: {workerState.process.pid})"
            )

    @convertAsyncioMethodToDeferred
    async def start(self):
        assert not self._isRunning, "Workers are already running"

        logger.info(f"Starting {self.config.numWorkers} workers")

        await self._connectToValkeyAsync()
        await self._maintainWorkerCountAsync()
        self._isRunning = True

    @convertAsyncioMethodToDeferred
    async def shutdown(self):
        if not self._isRunning:
            logging.debug("Workers are not running")
            return

        self._shutdownRequested = True
        logger.info("Stopping all workers")
        workerIds = list(self._workers.keys())

        for workerId in workerIds:
            self._stopWorkerGracefully(workerId)

        await self._disconnectFromValkeyAsync()
        self._isRunning = False

    def _stopWorkerGracefully(self, workerId: str):
        if workerId not in self._workers:
            return

        workerState = self._workers[workerId]
        if not workerState.process.is_alive():
            if workerId in self._workers:
                del self._workers[workerId]
            return

        logger.info(f"Sending SIGTERM to worker {workerId}")
        workerState.process.terminate()

        # Wait up to 10 seconds for a graceful shutdown
        workerState.process.join(timeout=10)

        if workerState.process.is_alive():
            logging.warning(
                f"Worker {workerId} did not shut down gracefully, sending SIGKILL"
            )
            workerState.process.kill()
            workerState.process.join(timeout=5)

            if workerState.process.is_alive():
                logging.error(f"Worker {workerId} still alive after SIGKILL")

        if workerId in self._workers:
            del self._workers[workerId]
        logger.info(f"Worker {workerId} stopped")

    def _stopWorker(self, workerId: str):
        # Legacy method for recycling - use graceful shutdown
        self._stopWorkerGracefully(workerId)

    def getWorkerStatus(self) -> List[Dict[str, Any]]:
        status = []

        for workerId, workerState in self._workers.items():
            try:

                status.append(
                    {
                        "worker_id": workerId,
                        "pid": workerState.process.pid,
                        "is_alive": workerState.process.is_alive(),
                        "uptime_seconds": workerState.workerAgeSeconds,
                        "memory_mb": workerState.workerMemoryMb,
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                status.append(
                    {
                        "worker_id": workerId,
                        "pid": workerState.process.pid,
                        "is_alive": False,
                        "uptime_seconds": 0,
                        "memory_mb": 0,
                    }
                )

        return status
