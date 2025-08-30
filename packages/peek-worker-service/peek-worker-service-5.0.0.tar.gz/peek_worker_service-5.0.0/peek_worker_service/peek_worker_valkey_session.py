import asyncio
import functools
from typing import Any
from urllib.parse import parse_qs
from urllib.parse import urlparse

from twisted.internet.defer import Deferred
from valkey.asyncio import ConnectionPool
from valkey.asyncio import UnixDomainSocketConnection
from valkey.asyncio import Valkey


class PeekWorkerValkeySession:
    def __init__(self, connectionPool: ConnectionPool):
        self.connectionPool = connectionPool
        self.client = None

    async def __aenter__(self):
        self.client = Valkey(connection_pool=self.connectionPool)
        return self

    async def __aexit__(self, excType, excVal, excTb):
        if self.client:
            await self.client.aclose()
            self.client = None

    def __getattr__(self, name: str) -> Any:
        if self.client is None:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager."
            )
        return getattr(self.client, name)


class PeekValkeySessionFactory:
    def __init__(self, url: str, maxConnections: int):
        self.connectionPool = ConnectionPool(
            decode_responses=True,
            max_connections=maxConnections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_connect_timeout=3600,
            socket_timeout=3600,
            **urlToKwargs(url)
        )

    def __call__(self) -> PeekWorkerValkeySession:
        return PeekWorkerValkeySession(self.connectionPool)

    async def disconnectAsync(self):
        await self.connectionPool.disconnect()
        self.connectionPool = None

    @property
    def createdConnections(self) -> int:
        return len(getattr(self.connectionPool, "_created_connections", []))

    @property
    def availableConnections(self) -> int:
        return len(getattr(self.connectionPool, "_available_connections", []))

    @property
    def inUseConnections(self) -> int:
        return getattr(
            self.connectionPool, "_created_connections_count", 0
        ) - len(getattr(self.connectionPool, "_available_connections", []))

    @property
    def maxConnections(self) -> int:
        return self.connectionPool.max_connections


def convertAsyncioMethodToDeferred(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs) -> Deferred:
        return Deferred.fromFuture(asyncio.create_task(method(*args, **kwargs)))

    return wrapper


def urlToKwargs(url: str) -> dict:
    parsed = urlparse(url)
    kwargs = {}

    if parsed.scheme == "unix":
        kwargs["connection_class"] = UnixDomainSocketConnection
        kwargs["path"] = parsed.path

        if parsed.query:
            query_params = parse_qs(parsed.query)
            if "db" in query_params:
                kwargs["db"] = int(query_params["db"][0])

    elif parsed.scheme in ["valkey", "redis"]:
        kwargs["host"] = parsed.hostname
        kwargs["port"] = parsed.port or 6379
        kwargs["db"] = (
            int(parsed.path.lstrip("/"))
            if parsed.path and parsed.path != "/"
            else 0
        )

        if parsed.password:
            kwargs["password"] = parsed.password
        if parsed.username:
            kwargs["username"] = parsed.username

    return kwargs
