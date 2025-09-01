"""
Test ID (TID) management using contextvars for test isolation.
"""

import uuid
from contextvars import ContextVar
from typing import Optional

# This key name is defined in github.com/YoshikiShibata/courier/tid
# key name must be same as the one in your golang code.
tid_header_key = "courier-testing-id"

_tid_context: ContextVar[Optional[str]] = ContextVar("TID", default=None)


def new_tid() -> str:
    return str(uuid.uuid4())


def set_tid(tid: str) -> None:
    _tid_context.set(tid)


def extract_tid() -> Optional[str]:
    return _tid_context.get()
