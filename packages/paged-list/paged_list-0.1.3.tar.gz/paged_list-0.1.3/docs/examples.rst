Examples
========

Basic Usage
-----------

Here's a simple example of using PagedList:

.. literalinclude:: ../examples/basic_usage.py
   :language: python
   :caption: Basic Usage Example

Advanced Usage
--------------

Context Manager
~~~~~~~~~~~~~~~

.. code-block:: python

   from paged_list import PagedList

   with PagedList(chunk_size=10000) as pl:
       # Add lots of data
       for i in range(1000000):
           pl.append({"data": f"item_{i}"})

       # Process data
       result = pl[500000:500010]

       # Automatic cleanup on exit

Custom Serialization
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Serialize complex Python objects to JSON strings
   pl.append({
       "id": 1,
       "metadata": {"tags": ["python", "data"], "active": True},
       "scores": [1.2, 3.4, 5.6],
   })

   pl.serialize()  # Converts lists, dicts, and bools to JSON strings

Parallel Processing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Process data in parallel across chunks
   def process_record(record):
       record["processed"] = True
       record["timestamp"] = "2024-01-01"
       return record

   pl.map(process_record, max_workers=4)  # Use 4 threads

Use Cases
---------

- **Large Dataset Processing**: Handle datasets that don't fit in memory
- **Data Pipelines**: Process streaming data with automatic disk overflow
- **ETL Operations**: Transform large datasets chunk by chunk
- **Data Analysis**: Analyze large datasets without memory constraints
- **Caching**: Implement persistent, memory-efficient caches
