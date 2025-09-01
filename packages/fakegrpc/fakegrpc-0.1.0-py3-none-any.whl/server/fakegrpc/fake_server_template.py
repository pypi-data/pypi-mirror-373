"""
Template for generating fake gRPC servers.
"""

FAKE_SERVER_TEMPLATE = '''# This code is auto-generated. DO NOT EDIT.

"""
Fake gRPC server implementation for {service_name} service.
"""

from typing import Optional, Callable
from server.fakegrpc.fake_server_stub import GRPCServerStub
from {import_path} import {import_name}
import tid.tid


class {service_name}Server({import_name}.{service_name}Base):
    def __init__(self):
        self.srv_stub = GRPCServerStub()
{method_implementations}
    def clear_all_responses(self, tid: str):
        """Clear all registered responses for a specific TID."""
        self.srv_stub.clear_all_responses(tid)
{setter_methods}
'''

METHOD_IMPLEMENTATION_TEMPLATE = """
    async def {method_name}(
        self, {request_param_name}: {import_name}.{request_type_name}
    ) -> {import_name}.{response_type_name}:
        current_tid = tid.tid.extract_tid()
        if not current_tid:
            raise ValueError("No TID found in context for {method_name}")

        return await self.srv_stub.handle_request(
            current_tid,
            "{rpc_name}",
            {request_param_name}
        )"""

SETTER_METHOD_TEMPLATE = """
    def set_{method_name}_response(
        self,
        tid: str,
        response: Optional[{import_name}.{response_type_name}] = None,
        error: Optional[Exception] = None
    ):
        self.srv_stub.set_response(tid, "{rpc_name}", response, error)

    def set_{method_name}_response_creator(
        self,
        tid: str,
        creator: Callable[[{import_name}.{request_type_name}], tuple[Optional[{import_name}.{response_type_name}], Optional[Exception]]]
    ):
        self.srv_stub.set_response_creator(tid, "{rpc_name}", creator)"""
