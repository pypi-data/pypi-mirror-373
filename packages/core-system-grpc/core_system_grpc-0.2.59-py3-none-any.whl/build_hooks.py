import subprocess
import re
import tomllib
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Custom build hook to compile proto files before building."""

    def initialize(self, version, build_data, target_name):
        """Initialize the build hook."""
        if target_name in ("wheel", "sdist"):
            self.compile_proto_files()
            self.update_version_in_init()

    def update_version_in_init(self):
        """Update version in __init__.py to match pyproject.toml"""
        try:
            # Read version from pyproject.toml
            with open("pyproject.toml", "rb") as f:
                config = tomllib.load(f)
                version = config["project"]["version"]

            # Update version in __init__.py
            init_file = Path("generated/python/__init__.py")
            if init_file.exists():
                content = init_file.read_text()
                # Update __version__ line
                content = re.sub(
                    r'__version__ = ".*?"', f'__version__ = "{version}₩"', content
                )
                init_file.write_text(content)
                print(f"Updated __init__.py version to {version}")
            else:
                print("Warning: __init__.py not found, skipping version update")
        except Exception as e:
            print(f"Warning: Could not update version in __init__.py: {e}")

    def compile_proto_files(self):
        """Compile proto files to Python."""
        proto_dir = Path("proto")
        python_out = Path("generated/python")

        if not proto_dir.exists():
            return

        # Create output directory
        python_out.mkdir(parents=True, exist_ok=True)

        # Find all proto files
        proto_files = list(proto_dir.rglob("*.proto"))

        if not proto_files:
            return

        print("Compiling proto files...")

        # Compile proto files
        for proto_file in proto_files:
            try:
                subprocess.run(
                    [
                        "python",
                        "-m",
                        "grpc_tools.protoc",
                        "--proto_path=proto",
                        "--python_out=generated/python",
                        "--grpc_python_out=generated/python",
                        "--pyi_out=generated/python",
                        str(proto_file),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Error compiling {proto_file}: {e}")
                print(f"stdout: {e.stdout}")
                print(f"stderr: {e.stderr}")
                raise

        # Fix imports in generated files
        self.fix_imports(python_out)

        # Create __init__.py files
        self.create_init_files(python_out)

        print("Proto compilation completed!")

    def fix_imports(self, python_out):
        """Fix relative imports in generated files."""
        for grpc_file in python_out.rglob("*_grpc.py"):
            try:
                with open(grpc_file, "r") as f:
                    content = f.read()

                # Fix imports
                old_import = "import {}_pb2 as".format(
                    grpc_file.stem.replace("_grpc", "")
                )
                new_import = "from . import {}_pb2 as".format(
                    grpc_file.stem.replace("_grpc", "")
                )
                content = content.replace(old_import, new_import)

                with open(grpc_file, "w") as f:
                    f.write(content)
            except Exception as e:
                print(f"Warning: Could not fix imports in {grpc_file}: {e}")

    def create_init_files(self, python_out):
        """Create __init__.py files in all directories."""
        for directory in python_out.rglob("*"):
            if directory.is_dir():
                init_file = directory / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
