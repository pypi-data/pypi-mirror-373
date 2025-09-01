import asyncio
import ssl
from typing import Callable, Optional, TypeVar, Union

from grpclib.client import Channel

T = TypeVar("T")


class LazyInitializedClient[T]:
    def __init__(
        self,
        client_factory: Callable[[Channel], T],
        host: str,
        port: int,
        use_ssl: bool = False,
    ):
        self._lazy_loaded_client: Optional[T] = None
        self._client_factory = client_factory
        self._lock = asyncio.Lock()
        self._host = host
        self._port = port
        self._use_ssl = use_ssl

    async def get_client(self) -> T:
        # Channel の初期化時に asyncio.get_event_loop が必要で、同期 context では実行できない。
        # そのため、非同期 context で（初期）遅延作成する必要
        async with self._lock:
            if self._lazy_loaded_client is None:
                ssl_context: Union[bool, ssl.SSLContext, None] = None
                if self._use_ssl:
                    # TLS/SSL接続を有効にする
                    ssl_context = True

                channel = Channel(self._host, self._port, ssl=ssl_context)
                self._lazy_loaded_client = self._client_factory(channel)
            return self._lazy_loaded_client
