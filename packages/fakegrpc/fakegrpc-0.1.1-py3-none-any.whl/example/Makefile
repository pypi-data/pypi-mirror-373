SERVICES = warehouse_v1 shipping_v1 shop_v1

.PHONY: compile
compile:
	mkdir -p api
	PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:$$PATH" protoc -I proto --python_betterproto_out=api $(shell find proto -name "*.proto")

.PHONY: genfakes
genfakes: $(SERVICES)

$(SERVICES):
	cd .. && uv run example/scripts/$@.py > example/fakeservers/$@.py
	@if command -v black >/dev/null 2>&1; then \
		echo "Formatting generated code with black..."; \
		black fakeservers/$@.py || true; \
	fi

.PHONY: run
run:
	cd .. && PYTHONUNBUFFERED=1 uv run example/main.py

.PHONY: test
test:
	cd .. && uv run pytest example/e2etest/ -v -s --disable-warnings
