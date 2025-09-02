"""
BirdCount - Bird call counting and analysis tool

A Python package for processing, analyzing, and counting bird calls from audio recordings.
"""

__version__ = "0.1.0"
__author__ = "Sean Rowland"
__email__ = "seanwrowland@gmail.com"

from . import audio
from . import ml
from . import pipelines
from . import reports
from . import config

__all__ = [
    "audio",
    "ml", 
    "pipelines",
    "reports",
    "config"
]
