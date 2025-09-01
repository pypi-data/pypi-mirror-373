# This code is auto-generated. DO NOT EDIT.

"""
Fake gRPC server implementation for Warehouse service.
"""

from typing import Optional, Callable
from fakegrpc.server.fakegrpc.fake_server_stub import GRPCServerStub
from example.api.warehouse import v1
from fakegrpc.tid.tid import extract_tid


class WarehouseServer(v1.WarehouseBase):
    def __init__(self):
        self.srv_stub = GRPCServerStub()

    async def list_product_inventories(
        self, list_product_inventories_request: v1.ListProductInventoriesRequest
    ) -> v1.ListProductInventoriesResponse:
        current_tid = extract_tid()
        if not current_tid:
            raise ValueError("No TID found in context for list_product_inventories")

        return await self.srv_stub.handle_request(
            current_tid,
            "ListProductInventories",
            list_product_inventories_request
        )
    async def ship_product(
        self, ship_product_request: v1.ShipProductRequest
    ) -> v1.ShipProductResponse:
        current_tid = extract_tid()
        if not current_tid:
            raise ValueError("No TID found in context for ship_product")

        return await self.srv_stub.handle_request(
            current_tid,
            "ShipProduct",
            ship_product_request
        )
    def clear_all_responses(self, tid: str):
        """Clear all registered responses for a specific TID."""
        self.srv_stub.clear_all_responses(tid)

    def set_list_product_inventories_response(
        self,
        tid: str,
        response: Optional[v1.ListProductInventoriesResponse] = None,
        error: Optional[Exception] = None
    ):
        self.srv_stub.set_response(tid, "ListProductInventories", response, error)

    def set_list_product_inventories_response_creator(
        self,
        tid: str,
        creator: Callable[[v1.ListProductInventoriesRequest], tuple[Optional[v1.ListProductInventoriesResponse], Optional[Exception]]]
    ):
        self.srv_stub.set_response_creator(tid, "ListProductInventories", creator)
    def set_ship_product_response(
        self,
        tid: str,
        response: Optional[v1.ShipProductResponse] = None,
        error: Optional[Exception] = None
    ):
        self.srv_stub.set_response(tid, "ShipProduct", response, error)

    def set_ship_product_response_creator(
        self,
        tid: str,
        creator: Callable[[v1.ShipProductRequest], tuple[Optional[v1.ShipProductResponse], Optional[Exception]]]
    ):
        self.srv_stub.set_response_creator(tid, "ShipProduct", creator)

