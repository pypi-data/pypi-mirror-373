from example.api.warehouse import v1
from example.internal.infra._client import LazyInitializedClient


class WarehouseClient:
    def __init__(
        self,
        host: str,
        port: int,
    ):
        self.lazy_initialized_client = LazyInitializedClient(
            v1.WarehouseStub, host, port, use_ssl=False
        )

    async def get_client(self):
        return await self.lazy_initialized_client.get_client()
