from .client import OuterportClient, AsyncOuterportClient
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("outerport")
except PackageNotFoundError:
    # Package is not installed
    __version__ = "0.0.0"  # or some default version

__all__ = ["OuterportClient", "AsyncOuterportClient", "__version__"]
