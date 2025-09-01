try:
    from ._version import __version__  # noqa: F401
except ImportError:
    __version__ = "0+unknown"

__all__ = [
    "communication_utils",
    "logging_lib",
    "encoding_utils",
    "power_consumption",
    "vdb_utils",
]
