import sys

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # For Python < 3.8
    from importlib_metadata import PackageNotFoundError, version


def check_modules(modules, required_pkg):
    missing = []
    for module in modules:
        try:
            _ = version(module)
        except PackageNotFoundError:
            missing.append(module)

    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print(f"Install them using: \n\n pip install {required_pkg}")
        sys.exit(1)

    return True
