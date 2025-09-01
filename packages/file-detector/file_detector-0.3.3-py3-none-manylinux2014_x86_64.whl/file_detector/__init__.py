from .detect import detect_file, detect_buffer, is_text, FileCategory, FileSubtype, Kind

__version__ = "0.3.3"
__version_info__ = tuple(int(i) for i in __version__.split('.'))
__all__ = [
    "detect_file",
    "detect_buffer",
    "is_text",
    "FileCategory",
    "FileSubtype",
    "Kind",
]
