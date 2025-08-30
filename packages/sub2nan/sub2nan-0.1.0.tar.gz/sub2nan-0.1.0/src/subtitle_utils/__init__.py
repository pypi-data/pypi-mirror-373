"""
subtitle_utils - A lightweight Python library for handling subtitle files.

This library provides simple and efficient tools for working with subtitle formats,
starting with SRT support and planned expansion to WebVTT and SMI formats.
"""

__version__ = "0.1.0"
__author__ = "2nan"
__email__ = "dame2623@gmail.com"

from .srt_handler import SRTHandler
from .exceptions import SubtitleError, SubtitleParseError, SubtitleFileError

__all__ = [
    "SRTHandler",
    "SubtitleError",
    "SubtitleParseError",
    "SubtitleFileError",
    "__version__",
]
