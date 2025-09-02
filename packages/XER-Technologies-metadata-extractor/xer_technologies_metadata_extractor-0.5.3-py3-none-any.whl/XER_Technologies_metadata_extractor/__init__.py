"""
XER Technologies Metadata Extractor

A Python package for extracting and processing metadata from XER CSV files.
Supports both local file processing and in-memory data.
Includes postprocessing pipeline integration for column renaming and power calculations.
"""

from .extract import MetadataExtractor
from .validation import FileValidator, ValidationResult
from .metadata_config import MetadataConfig, MetadataField, metadata_config
from .metadata_calculator import MetadataCalculator, metadata_calculator
from .postprocessing_integration import PostProcessingIntegration, postprocessing_integration

__version__ = "0.5.3"
__author__ = "Jakob Wiren"
__email__ = "jakob.wiren@xer-tech.com"

__all__ = [
    "MetadataExtractor",
    "FileValidator",
    "ValidationResult",
    "MetadataConfig",
    "MetadataField",
    "metadata_config",
    "MetadataCalculator",
    "metadata_calculator",
    "PostProcessingIntegration",
    "postprocessing_integration",
]
