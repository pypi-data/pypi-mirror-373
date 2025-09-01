# This code is auto-generated. DO NOT EDIT.

"""
Fake gRPC server implementation for Shipping service.
"""

from typing import Optional, Callable
from fakegrpc.server.fakegrpc.fake_server_stub import GRPCServerStub
from example.api.shipping import v1
from fakegrpc.tid.tid import extract_tid


class ShippingServer(v1.ShippingBase):
    def __init__(self):
        self.srv_stub = GRPCServerStub()

    async def create(
        self, create_shipping_request: v1.CreateShippingRequest
    ) -> v1.CreateShippingResponse:
        current_tid = extract_tid()
        if not current_tid:
            raise ValueError("No TID found in context for create")

        return await self.srv_stub.handle_request(
            current_tid,
            "Create",
            create_shipping_request
        )
    async def status(
        self, shipping_status_request: v1.ShippingStatusRequest
    ) -> v1.ShippingStatusResponse:
        current_tid = extract_tid()
        if not current_tid:
            raise ValueError("No TID found in context for status")

        return await self.srv_stub.handle_request(
            current_tid,
            "Status",
            shipping_status_request
        )
    def clear_all_responses(self, tid: str):
        """Clear all registered responses for a specific TID."""
        self.srv_stub.clear_all_responses(tid)

    def set_create_response(
        self,
        tid: str,
        response: Optional[v1.CreateShippingResponse] = None,
        error: Optional[Exception] = None
    ):
        self.srv_stub.set_response(tid, "Create", response, error)

    def set_create_response_creator(
        self,
        tid: str,
        creator: Callable[[v1.CreateShippingRequest], tuple[Optional[v1.CreateShippingResponse], Optional[Exception]]]
    ):
        self.srv_stub.set_response_creator(tid, "Create", creator)
    def set_status_response(
        self,
        tid: str,
        response: Optional[v1.ShippingStatusResponse] = None,
        error: Optional[Exception] = None
    ):
        self.srv_stub.set_response(tid, "Status", response, error)

    def set_status_response_creator(
        self,
        tid: str,
        creator: Callable[[v1.ShippingStatusRequest], tuple[Optional[v1.ShippingStatusResponse], Optional[Exception]]]
    ):
        self.srv_stub.set_response_creator(tid, "Status", creator)

