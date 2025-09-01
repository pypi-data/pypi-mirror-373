"""fakegrpc - A E2E testing framework for services based on gRPC"""

__version__ = "0.1.1"

from . import server
from . import tid

__all__ = [
    "server",
    "tid",
]
