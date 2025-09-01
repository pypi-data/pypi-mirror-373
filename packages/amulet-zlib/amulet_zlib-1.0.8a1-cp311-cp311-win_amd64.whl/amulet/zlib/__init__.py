from typing import TYPE_CHECKING
import logging as _logging

from . import _version

__version__ = _version.get_versions()["version"]

if TYPE_CHECKING:

    class ZipBombException(RuntimeError):
        pass

    def get_max_decompression_size() -> int: ...
    def set_max_decompression_size(max_decompression_size: int) -> None: ...

    def decompress_zlib_gzip(src: bytes) -> bytes: ...
    def compress_zlib(src: bytes) -> bytes: ...
    def compress_gzip(src: bytes) -> bytes: ...


# init a default logger
_logging.basicConfig(level=_logging.INFO, format="%(levelname)s - %(message)s")


def _init() -> None:
    import os
    import sys
    import ctypes

    if sys.platform == "win32":
        lib_path = os.path.join(os.path.dirname(__file__), "amulet_zlib.dll")
    elif sys.platform == "darwin":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_zlib.dylib")
    elif sys.platform == "linux":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_zlib.so")
    else:
        raise RuntimeError(f"Unsupported platform {sys.platform}")

    # Load the shared library
    ctypes.cdll.LoadLibrary(lib_path)

    from ._amulet_zlib import init

    init(sys.modules[__name__])


_init()
