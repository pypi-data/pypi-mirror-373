import grpclib

from example.api.shop import v1 as shop_v1
from example.api.warehouse import v1 as warehouse_v1
from example.e2etest import main_test
from example.e2etest.main_test import E2ETestCase, fake_warehouse_server
from example.e2etest.shop_client import new_shop_client
from example.e2etest.test import Test


class TestListProducts(E2ETestCase):
    async def test_list_products_invalid_argument(self):
        t = Test("test_list_products_invalid_argument")
        client = new_shop_client(t, main_test.target_server_port)

        # act & assert
        with t.assert_grpc_code(grpclib.const.Status.INVALID_ARGUMENT):
            await client.list_product_inventories(
                shop_v1.ListProductInventoriesRequest(num_of_products=0)
            )

    async def test_list_products_deadline_exceeded(self):
        t = Test("test_list_products_deadline_exceeded")
        fake_warehouse_server.set_list_product_inventories_response(
            t.tid,
            error=grpclib.GRPCError(
                grpclib.const.Status.DEADLINE_EXCEEDED,
                "deadline exceeded",
            ),
        )
        client = new_shop_client(t, main_test.target_server_port)

        # act & assert
        with t.assert_grpc_code(grpclib.const.Status.DEADLINE_EXCEEDED):
            await client.list_product_inventories(
                shop_v1.ListProductInventoriesRequest(num_of_products=10)
            )

    async def test_list_products(self):
        t = Test("check tid propagation")

        fake_warehouse_server.set_list_product_inventories_response(
            t.tid,
            warehouse_v1.ListProductInventoriesResponse(
                product_inventories=[
                    warehouse_v1.ProductInventory(
                        number="1",
                        name="product1",
                        price=100,
                        quantity_available=10,
                    ),
                ],
            ),
        )

        client = new_shop_client(t, main_test.target_server_port)

        # act
        res = await client.list_product_inventories(
            shop_v1.ListProductInventoriesRequest(num_of_products=10)
        )

        # assert
        assert len(res.product_inventories) == 1
        assert res.product_inventories[0].number == "1"
        assert res.product_inventories[0].name == "product1"
        assert res.product_inventories[0].price == 100
        assert res.product_inventories[0].quantity_available == 10
