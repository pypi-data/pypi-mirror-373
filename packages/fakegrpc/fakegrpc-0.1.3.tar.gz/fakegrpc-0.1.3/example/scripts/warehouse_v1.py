#!/usr/bin/env python3
"""
Generate fake server for Warehouse service.
"""

from example.api.warehouse import v1 as warehouse_v1
from fakegrpc.server import TemplateConfig, generate


def main():
    config = TemplateConfig(
        service_name="Warehouse",
        import_path="example.api.warehouse",
        import_name="v1",
        service_base_class=warehouse_v1.WarehouseBase,
        methods=[],
    )

    print(generate(config))


if __name__ == "__main__":
    main()
