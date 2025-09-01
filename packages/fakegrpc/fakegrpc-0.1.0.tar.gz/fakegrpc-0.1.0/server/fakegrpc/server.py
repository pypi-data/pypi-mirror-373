import asyncio
import threading

from grpclib._typing import IServable
from grpclib.events import RecvRequest, listen
from grpclib.server import Server

from tid import grpc_propagator


class FakeServers:
    def __init__(self, port: int):
        self._fake_server: Server | None = None
        self._threading_event = threading.Event()
        self._port = port

    def start(self, services: list[IServable]):
        async def main():
            # NOTE: Server はなぜか MainThread ではなくこちらの thread 内で作成しないとうまく動かない
            self._fake_server = Server(services)
            listen(self._fake_server, RecvRequest, grpc_propagator.set_tid_in_context)
            await self._fake_server.start("0.0.0.0", self._port)
            print(f"【FakeServers】: fake server started on port {self._port}")
            await self._wait_for_threading_event(self._threading_event, 1.0)

        asyncio.run(main())

    async def _wait_for_threading_event(
        self, threading_event: threading.Event, poll_interval: float
    ):
        while not threading_event.is_set():
            await asyncio.sleep(poll_interval)

    def close(self):
        if self._fake_server is not None:
            self._fake_server.close()  # force shotdown
        self._threading_event.set()
