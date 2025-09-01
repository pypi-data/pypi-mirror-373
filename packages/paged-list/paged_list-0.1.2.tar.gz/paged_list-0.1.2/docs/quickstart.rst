Quick Start
===========

Installation
------------

Install paged-list from PyPI:

.. code-block:: bash

   pip install paged-list

Requirements
------------

- Python 3.9 or higher
- No external dependencies for core functionality

Basic Usage
-----------

.. code-block:: python

   from paged_list import PagedList

   # Create a disk-backed list
   with PagedList(chunk_size=50000) as pl:
       # Add data - will automatically chunk to disk when needed
       for i in range(100000):
           pl.append({"id": i, "value": f"item_{i}", "score": i * 1.5})

       # Access data like a regular list
       print(pl[0])  # First item
       print(pl[-1])  # Last item
       print(pl[1000:1010])  # Slice of 10 items

       # Apply transformations
       def double_score(record):
           record["score"] *= 2
           return record

       pl.map(double_score)

Features
--------

- **Memory Efficient**: Only keeps a small portion of data in memory
- **Automatic Chunking**: Transparently splits large datasets into manageable chunks
- **List-like Interface**: Supports indexing, slicing, and iteration like regular Python lists
- **Parallel Processing**: Built-in map and serialization functions with multi-threading support
- **Type Safety**: Designed for dictionaries with comprehensive type hints
- **Context Manager**: Automatic cleanup of temporary files
