# This code is auto-generated. DO NOT EDIT.

"""
Fake gRPC server implementation for Shop service.
"""

from typing import Optional, Callable
from server.fakegrpc.fake_server_stub import GRPCServerStub
from example.api.shop import v1
import tid.tid


class ShopServer(v1.ShopBase):
    def __init__(self):
        self.srv_stub = GRPCServerStub()

    async def create_order(
        self, create_order_request: v1.CreateOrderRequest
    ) -> v1.CreateOrderResponse:
        current_tid = tid.tid.extract_tid()
        if not current_tid:
            raise ValueError("No TID found in context for create_order")

        return await self.srv_stub.handle_request(
            current_tid, "CreateOrder", create_order_request
        )

    async def get_shipping_status(
        self, get_shipping_status_request: v1.GetShippingStatusRequest
    ) -> v1.GetShippingStatusResponse:
        current_tid = tid.tid.extract_tid()
        if not current_tid:
            raise ValueError("No TID found in context for get_shipping_status")

        return await self.srv_stub.handle_request(
            current_tid, "GetShippingStatus", get_shipping_status_request
        )

    async def list_product_inventories(
        self, list_product_inventories_request: v1.ListProductInventoriesRequest
    ) -> v1.ListProductInventoriesResponse:
        current_tid = tid.tid.extract_tid()
        if not current_tid:
            raise ValueError("No TID found in context for list_product_inventories")

        return await self.srv_stub.handle_request(
            current_tid, "ListProductInventories", list_product_inventories_request
        )

    def clear_all_responses(self, tid: str):
        """Clear all registered responses for a specific TID."""
        self.srv_stub.clear_all_responses(tid)

    def set_create_order_response(
        self,
        tid: str,
        response: Optional[v1.CreateOrderResponse] = None,
        error: Optional[Exception] = None,
    ):
        self.srv_stub.set_response(tid, "CreateOrder", response, error)

    def set_create_order_response_creator(
        self,
        tid: str,
        creator: Callable[
            [v1.CreateOrderRequest],
            tuple[Optional[v1.CreateOrderResponse], Optional[Exception]],
        ],
    ):
        self.srv_stub.set_response_creator(tid, "CreateOrder", creator)

    def set_get_shipping_status_response(
        self,
        tid: str,
        response: Optional[v1.GetShippingStatusResponse] = None,
        error: Optional[Exception] = None,
    ):
        self.srv_stub.set_response(tid, "GetShippingStatus", response, error)

    def set_get_shipping_status_response_creator(
        self,
        tid: str,
        creator: Callable[
            [v1.GetShippingStatusRequest],
            tuple[Optional[v1.GetShippingStatusResponse], Optional[Exception]],
        ],
    ):
        self.srv_stub.set_response_creator(tid, "GetShippingStatus", creator)

    def set_list_product_inventories_response(
        self,
        tid: str,
        response: Optional[v1.ListProductInventoriesResponse] = None,
        error: Optional[Exception] = None,
    ):
        self.srv_stub.set_response(tid, "ListProductInventories", response, error)

    def set_list_product_inventories_response_creator(
        self,
        tid: str,
        creator: Callable[
            [v1.ListProductInventoriesRequest],
            tuple[Optional[v1.ListProductInventoriesResponse], Optional[Exception]],
        ],
    ):
        self.srv_stub.set_response_creator(tid, "ListProductInventories", creator)
