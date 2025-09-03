"""
Generate fake gRPC server implementations.
"""

import inspect
from dataclasses import dataclass
from typing import List, get_type_hints

from fakegrpc.server.fakegrpc.fake_server_template import (
    FAKE_SERVER_TEMPLATE,
    METHOD_IMPLEMENTATION_TEMPLATE,
    SETTER_METHOD_TEMPLATE,
)


@dataclass
class RPCMethod:
    """Information about an RPC method."""

    name: str
    rpc_name: str
    request_param_name: str
    request_type_name: str
    response_type_name: str


@dataclass
class TemplateConfig:
    """Configuration for template generation."""

    service_name: str
    import_path: str
    import_name: str
    service_base_class: type
    methods: List[RPCMethod]


def generate(config: TemplateConfig) -> str:
    """
    Generate a fake server code based on the configuration.

    Args:
        config: Template configuration containing service information

    Returns:
        Generated fake server code as a string
    """
    # Extract methods from the service base class
    methods = _extract_methods(config.service_base_class)
    config.methods = methods

    # Generate method implementations
    method_implementations = ""
    for method in methods:
        method_implementations += METHOD_IMPLEMENTATION_TEMPLATE.format(
            method_name=method.name,
            request_param_name=method.request_param_name,
            request_type_name=method.request_type_name,
            response_type_name=method.response_type_name,
            import_name=config.import_name,
            rpc_name=method.rpc_name,
        )

    # Generate setter methods
    setter_methods = ""
    for method in methods:
        setter_methods += SETTER_METHOD_TEMPLATE.format(
            method_name=method.name,
            request_type_name=method.request_type_name,
            response_type_name=method.response_type_name,
            import_name=config.import_name,
            rpc_name=method.rpc_name,
        )

    # Generate final code
    return FAKE_SERVER_TEMPLATE.format(
        service_name=config.service_name,
        import_path=config.import_path,
        import_name=config.import_name,
        method_implementations=method_implementations,
        setter_methods=setter_methods,
    )


def _extract_methods(service_base_class: type) -> List[RPCMethod]:
    """Extract RPC methods from the service base class."""
    methods = []

    for name in dir(service_base_class):
        if not name.startswith("_") and name not in ["__init__", "__mapping__"]:
            method = getattr(service_base_class, name)
            if callable(method):
                # Get type hints to extract actual request/response types
                hints = get_type_hints(method)
                if "return" in hints:
                    # Extract parameter types
                    sig = inspect.signature(method)
                    params = list(sig.parameters.items())

                    if len(params) >= 2:  # self + request parameter
                        request_param_name = params[1][0]  # Get parameter name
                        request_type = hints.get(request_param_name)
                        response_type = hints.get("return")

                        if request_type and response_type:
                            # Extract just the class name from the type
                            request_type_name = getattr(
                                request_type, "__name__", str(request_type)
                            )
                            response_type_name = getattr(
                                response_type, "__name__", str(response_type)
                            )

                            # Convert method name to CamelCase for RPC name
                            rpc_name = "".join(
                                word.capitalize() for word in name.split("_")
                            )

                            methods.append(
                                RPCMethod(
                                    name=name,
                                    rpc_name=rpc_name,
                                    request_param_name=request_param_name,
                                    request_type_name=request_type_name,
                                    response_type_name=response_type_name,
                                )
                            )

    return methods
