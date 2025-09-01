import threading
from dataclasses import dataclass

from grpclib._typing import IServable

from server.command import CommandRunner
from server.fakegrpc.server import FakeServers
from server.grpc import sync_wait_for_grpc_server_ready


@dataclass
class E2ETestExecutor:
    target_server_runner: CommandRunner
    fake_servers: FakeServers
    fake_servers_thread: threading.Thread

    @classmethod
    def start_servers(
        cls,
        target_server_port: int,
        target_server_command: str,
        fake_server_port: int,
        fake_services: list[IServable],
        target_server_cwd: str | None,
    ):
        target_server_runner = CommandRunner(
            target_server_command, "target_server", cwd=target_server_cwd
        )
        target_server_thread = threading.Thread(
            target=target_server_runner.run,
        )
        target_server_thread.daemon = True
        target_server_thread.start()

        fake_servers = FakeServers(fake_server_port)
        fake_servers_thread = threading.Thread(
            target=fake_servers.start,
            args=(fake_services,),
        )
        fake_servers_thread.daemon = True
        fake_servers_thread.start()

        sync_wait_for_grpc_server_ready(target_server_port)
        return cls(
            target_server_runner=target_server_runner,
            fake_servers=fake_servers,
            fake_servers_thread=fake_servers_thread,
        )

    def stop_servers(self):
        self.target_server_runner.print_stdout()

        # 本当はこれなくても良いはず
        self.fake_servers.close()
        self.fake_servers_thread.join()

        # target server はちょっと面倒なので daemon thread 強制終了
