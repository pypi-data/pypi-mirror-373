"""
Metadata Curation Client

A lightweight API client for external partners to integrate with metadata curation platforms.
"""

from .curation_api_client import CurationAPIClient, PropertyType
from .source_manager import SourceManager, PropertyBuilder

__version__ = "0.1.0"
__all__ = ["CurationAPIClient", "PropertyType", "SourceManager", "PropertyBuilder"]
