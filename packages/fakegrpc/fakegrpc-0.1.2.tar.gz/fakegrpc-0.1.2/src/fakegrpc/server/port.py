import socket
import threading

port_lock = threading.Lock()


def find_free_port(exclude_ports: list[int]):
    start_port = 49152
    end_port = 65535
    with port_lock:
        for port in range(start_port, end_port + 1):
            if port in exclude_ports:
                continue

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    return port
                except socket.error:
                    continue
    raise ValueError("No free port found")
