from grpclib.client import Channel

from example.api.shop import v1 as shop_v1
from example.e2etest.test import Test
from fakegrpc.tid import tid


def new_shop_client(t: Test, port: int):
    channel = Channel("localhost", port)
    return shop_v1.ShopStub(channel, metadata={tid.tid_header_key: t.tid})
