import grpclib

from example.api.shop import v1
from example.api.warehouse import v1 as warehouse_v1
from example.internal.infra.shipping_client import ShippingClient
from example.internal.infra.warehouse_client import WarehouseClient
from tid import tid


class ShopServer(v1.ShopBase):
    def __init__(
        self,
        shipping_client: ShippingClient,
        warehouse_client: WarehouseClient,
    ):
        self.shipping_client = shipping_client
        self.warehouse_client = warehouse_client

    async def list_product_inventories(
        self, list_product_inventories_request: v1.ListProductInventoriesRequest
    ) -> v1.ListProductInventoriesResponse:
        if list_product_inventories_request.num_of_products == 0:
            raise grpclib.GRPCError(
                grpclib.const.Status.INVALID_ARGUMENT, "num_of_products"
            )

        try:
            metadata = {}
            if (id := tid.extract_tid()) is not None:
                metadata = {
                    tid.tid_header_key: id,
                }
            res = await (
                await self.warehouse_client.get_client()
            ).list_product_inventories(
                warehouse_v1.ListProductInventoriesRequest(
                    num_of_products=list_product_inventories_request.num_of_products,
                    page_token=list_product_inventories_request.page_token,
                ),
                metadata=metadata,
            )
        except grpclib.GRPCError as e:
            match e.status:
                case grpclib.const.Status.CANCELLED:
                    raise e
                case grpclib.const.Status.DEADLINE_EXCEEDED:
                    raise e
                case grpclib.const.Status.INVALID_ARGUMENT:
                    raise grpclib.GRPCError(
                        grpclib.const.Status.INVALID_ARGUMENT,
                        f"invalid argument: {e.message}",
                    )
                case _:
                    raise grpclib.GRPCError(
                        grpclib.const.Status.INTERNAL,
                        f"internal error: {e.message}",
                    )

        product_inventories = []
        for p in res.product_inventories:
            product_inventories.append(
                v1.ProductInventory(
                    number=p.number,
                    name=p.name,
                    price=p.price,
                    quantity_available=p.quantity_available,
                )
            )

        return v1.ListProductInventoriesResponse(
            product_inventories=product_inventories,
            next_page_token=res.next_page_token,
        )

    async def create_order(
        self, create_order_request: v1.CreateOrderRequest
    ) -> v1.CreateOrderResponse:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_shipping_status(
        self, get_shipping_status_request: v1.GetShippingStatusRequest
    ) -> v1.GetShippingStatusResponse:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)
