#!/usr/bin/env python3
"""
Generate fake server for Shipping service.
"""

from example.api.shipping import v1 as shipping_v1
from fakegrpc.server import TemplateConfig, generate


def main():
    config = TemplateConfig(
        service_name="Shipping",
        import_path="example.api.shipping",
        import_name="v1",
        service_base_class=shipping_v1.ShippingBase,
        methods=[],
    )

    print(generate(config))


if __name__ == "__main__":
    main()
