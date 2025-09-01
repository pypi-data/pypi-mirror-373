from contextlib import contextmanager

import grpclib
import pytest
from grpclib.const import Status

from tid import tid


class Test:
    def __init__(self, test_name: str):
        self.tid = tid.new_tid()
        self.test_name = test_name

    @contextmanager
    def assert_grpc_code(self, grpc_code: Status):
        with pytest.raises(grpclib.GRPCError) as e:
            yield
        assert e.value.status == grpc_code, f"{self.test_name} assert_grpc_code failed"
