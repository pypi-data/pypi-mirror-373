from grpclib.events import RecvRequest

from tid import tid


async def set_tid_in_context(event: RecvRequest):
    id = event.metadata.get(tid.tid_header_key.lower())
    if id:
        tid.set_tid(str(id))
