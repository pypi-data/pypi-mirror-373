from importlib.metadata import version as get_version


__version__ = get_version(__package__)


def main() -> None:
    print(f"Hello from psr-demo {__version__}")
