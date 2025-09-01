#!/usr/bin/env python3
"""
Generate fake server for Shop service.
"""

from example.api.shop import v1 as shop_v1

from fakegrpc.server import TemplateConfig, generate


def main():
    config = TemplateConfig(
        service_name="Shop",
        import_path="example.api.shop",
        import_name="v1",
        service_base_class=shop_v1.ShopBase,
        methods=[],
    )

    print(generate(config))


if __name__ == "__main__":
    main()
