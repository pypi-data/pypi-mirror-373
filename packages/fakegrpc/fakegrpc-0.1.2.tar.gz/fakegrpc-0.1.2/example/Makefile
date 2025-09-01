SERVICES = warehouse_v1 shipping_v1 shop_v1

.PHONY: compile
compile:
	mkdir -p api
	cd .. && PATH="$$(uv run python -c 'import sys; print("/".join(sys.executable.split("/")[:-1]))'):$$PATH" protoc -I example/proto --python_betterproto_out=example/api $$(find example/proto -name "*.proto")

.PHONY: genfakes
genfakes: $(SERVICES)

$(SERVICES):
	cd .. && PYTHONPATH=.:src uv run example/scripts/$@.py > example/fakeservers/$@.py
	@if command -v black >/dev/null 2>&1; then \
		echo "Formatting generated code with black..."; \
		black fakeservers/$@.py || true; \
	fi

.PHONY: run
run:
	cd .. && PYTHONPATH=.:src PYTHONUNBUFFERED=1 uv run example/main.py

.PHONY: test
test:
	cd .. && PYTHONPATH=.:src uv run pytest example/e2etest/ -v -s --disable-warnings
