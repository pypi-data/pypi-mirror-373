"""
paged-list: Professional disk-backed list implementation for Python.

This package provides PagedList, a high-performance disk-backed list class designed for
handling large datasets that exceed available memory. Data is intelligently chunked and
stored as pickle files on disk, with automatic memory management that loads only
relevant chunks when accessed.

Key Features:
    - Memory-efficient storage for datasets larger than available RAM
    - Transparent disk-backed operations with list-like interface
    - Automatic chunking with configurable chunk sizes
    - Parallel processing capabilities for data transformations
    - Context manager support for automatic resource cleanup
    - Type-safe operations with comprehensive type hints

Example:
    >>> from paged_list import PagedList
    >>> with PagedList(chunk_size=10000) as pl:
    ...     for i in range(1000000):
    ...         pl.append({"id": i, "data": f"record_{i}"})
    ...     print(f"Stored {len(pl)} records using minimal memory")
"""

__version__ = "0.1.3"
__author__ = "Christensen, Daniel"
__email__ = "christensen.daniel+pagedlist@outlook.com"

# Import main functionality
from .paged_list import PagedList

__all__ = ["PagedList"]
