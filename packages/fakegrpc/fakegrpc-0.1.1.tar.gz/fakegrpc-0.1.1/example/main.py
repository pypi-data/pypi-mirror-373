import asyncio
import contextvars
import os
import signal
import time

from grpclib.events import RecvRequest, SendTrailingMetadata, listen
from grpclib.server import Server

from example.internal.infra.shipping_client import ShippingClient
from example.internal.infra.warehouse_client import WarehouseClient
from example.internal.server.health import HealthServer
from example.internal.server.server import ShopServer
from tid import grpc_propagator


def new_grpc_services():
    shipping_service_addr = os.environ["SHIPPING_SERVICE_ADDR"]
    warehouse_service_addr = os.environ["WAREHOUSE_SERVICE_ADDR"]
    shipping_host, shipping_port = shipping_service_addr.rsplit(":", 1)
    warehouse_host, warehouse_port = warehouse_service_addr.rsplit(":", 1)

    return [
        ShopServer(
            shipping_client=ShippingClient(shipping_host, int(shipping_port)),
            warehouse_client=WarehouseClient(warehouse_host, int(warehouse_port)),
        ),
        HealthServer(),
    ]


# TODO: on_recv_request, on_send_trailing_metadata, services, port を引数にした起動関数を作成したい。
# fake server 起動時はそれをつかう感じ
request_start_time = contextvars.ContextVar("request_start_time")


async def on_recv_request(event: RecvRequest) -> None:
    metadata = {}
    for key, value in event.metadata.items():
        metadata[key] = value

    request_start_time.set(time.monotonic())


async def on_send_trailing_metadata(event: SendTrailingMetadata) -> None:
    request_end_time = time.monotonic()
    request_duration = request_end_time - request_start_time.get()

    print(f"request ends: {request_duration} seconds")


async def run_grpc_server(
    port: int,
    shutdown_event: asyncio.Event,
    graceful_shutdown_timeout: int,
    server: Server,
) -> None:
    host = "0.0.0.0"
    listen(server, RecvRequest, on_recv_request)
    listen(server, SendTrailingMetadata, on_send_trailing_metadata)

    print(f"gRPC: Starting server on {host}:{port}")
    await server.start(host=host, port=port)
    print(f"gRPC: Server started on {host}:{port}")

    # wait for shutdown signal
    await shutdown_event.wait()

    print("gRPC: Received shutdown signal")

    await _graceful_shutdown(server, graceful_shutdown_timeout)

    print("gRPC: Server has been shut down")


# server.wait_closed() で server._server が新しい connection を受け付けないようにしてくれると
# 思いきや、そうでなかったので、無理やり server._server を close する。
# なお、server.close() をよぶと handler.close() してしまい、
# 各リクエスト呼び出しで即時 asyncio.CancelledError が発生してしまうので、
# これはつかえない。
#
# 解決策として、server._server.close() だけを呼びつつ、handler.close せず handler.wait_closed() を
# 読んでくれる server.wait_closed() を読ぶようにした。
# 詳しくは server.wait_closed() とその周辺コード参照
async def _graceful_shutdown(server: Server, graceful_shutdown_timeout: int) -> None:
    print("gRPC: Graceful shutdown initiated...")

    if server._server is not None:
        server._server.close()  # stop accepting new connections
        if (
            server._server_closed_fut is not None
            and not server._server_closed_fut.done()
        ):
            # mark the server as closed
            server._server_closed_fut.set_result(None)

    for handler in server._handlers:
        handler.closing = True  # the handler rejects new requests

    try:
        print("gRPC: Waiting for existing requests to complete...")

        # wait for existing requests to complete
        await asyncio.wait_for(server.wait_closed(), timeout=graceful_shutdown_timeout)

        print("gRPC: Server shut down gracefully")
    except asyncio.TimeoutError:
        print(
            f"gRPC: Server graceful shutdown timed out after {graceful_shutdown_timeout} seconds"
        )
        # タイムアウト時は強制終了
        # handler側のリクエスト behaivior は asyncio.CancelledError を受け取る
        server.close()


# NOTE: only for local. use main.py instead for production.
if __name__ == "__main__":

    async def main():
        grpc_server_port = int(os.environ["GRPC_SERVER_PORT"])
        shutdown_event = asyncio.Event()

        def signal_handler():
            print("gRPC: Received shutdown signal")
            shutdown_event.set()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, signal_handler)
        loop.add_signal_handler(signal.SIGINT, signal_handler)

        server = Server(new_grpc_services())
        listen(server, RecvRequest, grpc_propagator.set_tid_in_context)
        await run_grpc_server(grpc_server_port, shutdown_event, 120, server)

    asyncio.run(main())
