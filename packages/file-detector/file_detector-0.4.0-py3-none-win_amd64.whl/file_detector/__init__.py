from .detect import (
    detect_file,
    detect_buffer,
    detect_file_mime_and_charset,
    detect_buffer_mime_and_charset,
    FileCategory,
    FileSubtype,
    Kind,
)

__version__ = "0.4.0"
__version_info__ = tuple(int(i) for i in __version__.split('.'))
__all__ = [
    "detect_file",
    "detect_buffer",
    "detect_file_mime_and_charset",
    "detect_buffer_mime_and_charset",
    "FileCategory",
    "FileSubtype",
    "Kind",
]
