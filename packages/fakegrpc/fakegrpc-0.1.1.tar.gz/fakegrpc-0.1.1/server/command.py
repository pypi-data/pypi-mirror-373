import subprocess
import threading


class CommandRunner:
    def __init__(self, command: str, thread_name: str, cwd: str | None):
        self._command = command
        self._thread_name = thread_name
        self._cwd = cwd
        self._threading_event = threading.Event()
        self._process: subprocess.Popen | None = None
        self._stdout_lines: list[str] = []
        self._stderr_lines: list[str] = []
        self._output_lock = threading.Lock()

    def run(self):
        print(f"[{self._thread_name}] command start: {self._command}")

        process = subprocess.Popen(
            self._command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 行バッファリング
            universal_newlines=True,
            cwd=self._cwd,
        )
        self._process = process

        def read_stdout():
            if process.stdout is None:
                self._stdout_lines.append("【ERROR】process.stdout is None")
                raise Exception("process.stdout is None")
            for line in iter(process.stdout.readline, ""):
                if line:
                    with self._output_lock:
                        self._stdout_lines.append(line.rstrip())
            process.stdout.close()

        stdout_thread = threading.Thread(target=read_stdout)
        stdout_thread.daemon = True

        # NOTE: _on_pytest 終了時に強制的に終了する
        stdout_thread.start()

    def print_stdout(self):
        with self._output_lock:
            if self._stdout_lines:
                print()
                print(f"\n[{self._thread_name}] === STDOUT ===")
                for line in self._stdout_lines:
                    print(line)
