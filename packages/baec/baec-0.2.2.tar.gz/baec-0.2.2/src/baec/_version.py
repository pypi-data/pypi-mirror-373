from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("baec")
# during CI
except PackageNotFoundError:
    __version__ = "0.2.2"
