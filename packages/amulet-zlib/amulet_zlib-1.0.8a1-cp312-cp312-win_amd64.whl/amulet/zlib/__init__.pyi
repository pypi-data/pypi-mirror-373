from __future__ import annotations

import typing

from . import _amulet_zlib, _version

__all__ = [
    "ZipBombException",
    "compiler_config",
    "compress_gzip",
    "compress_zlib",
    "decompress_zlib_gzip",
    "get_max_decompression_size",
    "set_max_decompression_size",
]

class ZipBombException(Exception):
    pass

def _init() -> None: ...
def compress_gzip(arg0: bytes) -> bytes:
    """
    Compress a bytes object using the gzip compression format.
    """

def compress_zlib(arg0: bytes) -> bytes:
    """
    Compress a bytes object using the zlib compression format.
    """

def decompress_zlib_gzip(arg0: bytes) -> bytes:
    """
    Decompress a bytes object compressed with either zlib or gzip.
    Raises ZipBombException if decompression requires more than the configured maximum decompression size.
    """

def get_max_decompression_size() -> int:
    """
    Get the configured maximum decompressed size in bytes. (Default 100MB)
    """

def set_max_decompression_size(arg0: typing.SupportsInt) -> None:
    """
    Set the configured maximum decompressed size in bytes.
    If decompression requires more memory than this it will raise ZipBombException.
    """

__version__: str
compiler_config: dict
