PROTO_DIR = proto
PYTHON_OUT = generated/python

# Auto-discover proto files
PROTO_FILES := $(shell find $(PROTO_DIR) -name "*.proto")

.PHONY: build-python clean install-deps build-package publish-package

build-python:
	@echo "Building Python gRPC client libraries..."
	@mkdir -p $(PYTHON_OUT)
	uv run python -m grpc_tools.protoc \
		--proto_path=$(PROTO_DIR) \
		--python_out=$(PYTHON_OUT) \
		--grpc_python_out=$(PYTHON_OUT) \
		--pyi_out=$(PYTHON_OUT) \
		$(PROTO_FILES)
	@find $(PYTHON_OUT) -name "*_grpc.py" -exec sed -i '' 's/import \([^.]*\)_pb2 as/from . import \1_pb2 as/g' {} \;
	@find $(PYTHON_OUT) -type d -exec touch {}/__init__.py \;
	@echo "Python build completed!"

clean:
	rm -rf $(PYTHON_OUT)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

install-deps:
	uv sync --dev

build-package:
	@echo "Building package with hatch..."
	uv run hatch build

publish-package:
	@echo "Publishing package to GitHub Packages..."
	@echo "Make sure you have GITHUB_TOKEN environment variable set"
	@echo "or configure ~/.pypirc with your GitHub token"
	uv run hatch publish --repo https://pypi.pkg.github.com/SaladLabInc/

# Alternative publish method using uv directly
publish-uv:
	@echo "Publishing package using uv..."
	@echo "Make sure you have GITHUB_TOKEN environment variable set"
	uv run python -m build
	uv run python -m twine upload --repository-url https://pypi.pkg.github.com/SaladLabInc/ dist/*

# Setup GitHub Packages authentication
setup-auth:
	@echo "Setting up GitHub Packages authentication..."
	@echo "Please create ~/.pypirc with the following content:"
	@echo "[distutils]"
	@echo "index-servers ="
	@echo "    github"
	@echo ""
	@echo "[github]"
	@echo "repository = https://pypi.pkg.github.com/SaladLabInc/"
	@echo "username = __token__"
	@echo "password = YOUR_GITHUB_TOKEN"