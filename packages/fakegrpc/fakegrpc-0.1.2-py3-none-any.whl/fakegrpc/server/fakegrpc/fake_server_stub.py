"""
GRPCServerStub provides basic primitives for a fake gRPC server.
"""

import asyncio
from typing import Any, Callable, Dict, Optional


class ResponseInfo:
    def __init__(
        self,
        response: Any = None,
        error: Optional[Exception] = None,
        creator: Optional[Callable] = None,
    ):
        self.response = response
        self.error = error
        self.creator = creator


class GRPCServerStub:
    def __init__(self):
        self._responses: Dict[str, ResponseInfo] = {}
        self._lock = asyncio.Lock()

    def set_response(
        self, tid: str, rpc_name: str, response: Any, error: Optional[Exception] = None
    ):
        key = f"{tid}:{rpc_name}"
        self._responses[key] = ResponseInfo(response=response, error=error)

    def set_response_creator(self, tid: str, rpc_name: str, creator: Callable):
        key = f"{tid}:{rpc_name}"
        self._responses[key] = ResponseInfo(creator=creator)

    async def handle_request(self, tid: str, rpc_name: str, request: Any) -> Any:
        key = f"{tid}:{rpc_name}"

        async with self._lock:
            response_info = self._responses.get(key)

        if response_info is None:
            raise RuntimeError(f"Response for {key} has not been set yet")

        # Handle dynamic creator
        if response_info.creator is not None:
            if asyncio.iscoroutinefunction(response_info.creator):
                return await response_info.creator(request)
            else:
                return response_info.creator(request)

        # Handle static response
        if response_info.error is not None:
            raise response_info.error
        return response_info.response

    def clear_all_responses(self, tid: str):
        prefix = f"{tid}:"
        keys_to_remove = [
            key for key in self._responses.keys() if key.startswith(prefix)
        ]
        for key in keys_to_remove:
            del self._responses[key]
