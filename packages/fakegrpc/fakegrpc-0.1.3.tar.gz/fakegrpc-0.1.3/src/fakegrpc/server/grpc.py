import asyncio

from grpclib.client import Channel

from fakegrpc.api.grpc.health import v1 as health_v1


def sync_wait_for_grpc_server_ready(port: int):
    asyncio.run(_wait_for_grpc_server_ready(port))


async def _wait_for_grpc_server_ready(port: int):
    channel = Channel("localhost", port)
    client = health_v1.HealthStub(channel)

    async with asyncio.timeout(15):
        while True:
            try:
                res = await client.check(health_v1.HealthCheckRequest(service=""))
            except Exception as e:
                print(f"Check failed: retry every second ... (error: {e})")
                await asyncio.sleep(1)
                continue

            match res.status:
                case health_v1.HealthCheckResponseServingStatus.SERVING:
                    return True
                case _:
                    print(
                        f"Check failed: retry every second ... (status: {res.status})"
                    )
                    await asyncio.sleep(1)
                    continue
