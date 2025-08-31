"""
Vector Generator Module for NetIntel-OCR v0.1.7

This module provides vector database optimization capabilities for extracted content.
By default (v0.1.7+), vector generation is ENABLED and creates:
- Vector-optimized markdown files
- LanceDB-ready chunks
- Comprehensive metadata
- Flattened JSON structures

Users can disable vector generation with --no-vector flag.
"""

from .generator import VectorGenerator
from .json_flattener import JSONFlattener
from .markdown_optimizer import MarkdownOptimizer
from .metadata_enricher import MetadataEnricher
from .content_filter import ContentFilter
from .chunker import Chunker
from .schema_generator import SchemaGenerator

__version__ = "0.1.7"
__all__ = [
    "VectorGenerator",
    "JSONFlattener", 
    "MarkdownOptimizer",
    "MetadataEnricher",
    "ContentFilter",
    "Chunker",
    "SchemaGenerator"
]