"""
Professional disk-backed list implementation for large-scale data processing.

PagedList provides a high-performance, memory-efficient alternative to Python lists
for handling datasets that exceed available system memory. The implementation
automatically manages data persistence through intelligent chunking and disk-backed
storage, maintaining list-like interface semantics while providing enterprise-grade
scalability for data processing workflows.

Features:
    - Transparent disk-backed storage with automatic memory management
    - Configurable chunking strategies for optimal performance
    - Parallel processing capabilities for data transformations
    - Enterprise-ready error handling and resource cleanup
    - Type-safe operations with comprehensive validation
"""

import atexit
import concurrent.futures
import json
import logging
import os
import pickle
import uuid
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Union,
)


class PagedList:
    """A disk-backed list-like object that stores most of its data on disk.

    When the list gets too large, data is chunked into `.pkl` files in the
    `data/` directory. When retrieving slices, only relevant chunks are loaded
    into memory.
    """

    def __init__(
        self,
        chunk_size: int = 50_000,
        disk_path: str = "data",
        auto_cleanup: bool = True,
    ):
        """Initialize a PagedList with configurable parameters.

        Args:
            chunk_size: Maximum items per chunk before flushing to disk
            disk_path: Directory to store chunk files
            auto_cleanup: Whether to automatically cleanup chunks on exit
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        self.chunk_size = chunk_size  # Max items per chunk
        self.disk_path = disk_path  # Directory to store chunk files
        self.chunk_count = 0  # Number of chunk files
        self._in_memory_list: List[
            Dict[str, Any]
        ] = []  # Temporary storage before flushing to disk
        self._file_identifier = (
            uuid.uuid4().hex
        )  # Random hex identifier for file names so they don't overwrite
        self._auto_cleanup = auto_cleanup

        # Ensure the storage directory exists
        os.makedirs(self.disk_path, exist_ok=True)
        if auto_cleanup:
            atexit.register(self.cleanup_chunks)  # Register cleanup on exit

    @property
    def is_empty(self) -> bool:
        """Return True if the list is empty."""
        return len(self) == 0

    @property
    def total_chunks(self) -> int:
        """Return the total number of chunks."""
        return self.chunk_count

    @property
    def in_memory_count(self) -> int:
        """Return the number of items currently in memory."""
        return len(self._in_memory_list)

    def __del__(self) -> None:
        """Destructor to ensure cleanup of chunk files."""
        try:
            if hasattr(self, "chunk_count") and hasattr(self, "disk_path"):
                self.cleanup_chunks()
        except AttributeError:
            pass  # Object may be partially initialized

    def append(self, data: Dict[str, Any]) -> None:
        """Appends an item to the list, flushing to disk if needed."""
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        self._in_memory_list.append(data)

        # When memory limit is hit, save to disk
        if len(self._in_memory_list) >= self.chunk_size:
            self._save_chunk_to_file()
            self._in_memory_list = []  # Reset in-memory list

    def extend(self, iterable: Iterable[Dict[str, Any]]) -> None:
        """Extends the list by adding multiple items at once."""
        for item in iterable:
            self.append(item)  # Leverage existing append logic with type checking

    def _save_chunk_to_file(self) -> None:
        """Saves the current in-memory list to a chunk file on disk."""
        chunk_file = os.path.join(
            self.disk_path, f"chunk_{self._file_identifier}_{self.chunk_count}.pkl"
        )
        with open(chunk_file, "wb") as f:
            pickle.dump(self._in_memory_list, f)
        logging.debug(f"Saved chunk {self.chunk_count} to {chunk_file}")
        self.chunk_count += 1

    def _load_chunk(self, chunk_index: int) -> List[Dict[str, Any]]:
        """Loads a specific chunk from disk."""
        chunk_file = os.path.join(
            self.disk_path, f"chunk_{self._file_identifier}_{chunk_index}.pkl"
        )
        if os.path.exists(chunk_file):
            with open(chunk_file, "rb") as f:
                loaded_data: List[Dict[str, Any]] = pickle.load(f)
                return loaded_data
        return []  # Return empty if file is missing

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterates over all records without loading them into memory."""
        for chunk_index in range(self.chunk_count):
            chunk_data = self._load_chunk(chunk_index)
            for record in chunk_data:
                yield record  # Yield one record at a time (memory efficient)

        # Yield remaining items in memory (not yet written to disk)
        for record in self._in_memory_list:
            yield record

    def __contains__(self, item: Dict[str, Any]) -> bool:
        """Check if an item is in the list."""
        return any(record == item for record in self)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Retrieve an item or slice from the disk-backed list."""
        if isinstance(index, int):  # Single index lookup
            # Handle negative indices
            if index < 0:
                index = len(self) + index

            # Check if index is in memory
            disk_items = self.chunk_count * self.chunk_size
            if index >= disk_items:
                # Item is in memory
                memory_index = index - disk_items
                if memory_index < len(self._in_memory_list):
                    return self._in_memory_list[memory_index]
                else:
                    raise IndexError("Index out of range")
            else:
                # Item is on disk
                chunk_index, inner_index = divmod(index, self.chunk_size)
                chunk_data = self._load_chunk(chunk_index)
                if inner_index < len(chunk_data):
                    return chunk_data[inner_index]
                else:
                    raise IndexError("Index out of range")

        elif isinstance(index, slice):  # Slice lookup
            start, stop, step = index.indices(len(self))

            results: List[Dict[str, Any]] = []
            for idx in range(start, stop, step if step else 1):
                item = self[idx]
                if isinstance(item, dict):
                    results.append(item)
                else:
                    # This shouldn't happen in normal usage, but handle it
                    results.extend(item)

            return results

        raise TypeError("Invalid index type. Must be int or slice.")

    def __setitem__(
        self,
        index: Union[int, slice],
        value: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> None:
        """Updates a value or replaces a slice in the disk-backed list."""
        if isinstance(index, int):  # Single index update
            # Handle negative indices
            if index < 0:
                index = len(self) + index

            # Check if index is in memory
            disk_items = self.chunk_count * self.chunk_size
            if index >= disk_items:
                # Item is in memory
                memory_index = index - disk_items
                if memory_index < len(self._in_memory_list):
                    if isinstance(value, list):
                        raise TypeError("Cannot assign a list to a single index")
                    self._in_memory_list[memory_index] = value
                else:
                    raise IndexError("Index out of range")
            else:
                # Item is on disk
                chunk_index, inner_index = divmod(index, self.chunk_size)
                chunk_file = os.path.join(
                    self.disk_path, f"chunk_{self._file_identifier}_{chunk_index}.pkl"
                )

                chunk_data = self._load_chunk(chunk_index)
                if inner_index >= len(chunk_data):
                    raise IndexError("Index out of range.")

                if isinstance(value, list):
                    raise TypeError("Cannot assign a list to a single index")
                chunk_data[inner_index] = value  # Replace value

                # Save the modified chunk
                with open(chunk_file, "wb") as f:
                    pickle.dump(chunk_data, f)
                logging.info(f"Updated index {index} in {chunk_file}")

        elif isinstance(index, slice):  # Slice update
            start, stop, step = index.indices(len(self))

            if step != 1:
                raise ValueError("Step slicing is not supported.")

            if not isinstance(value, list):
                raise TypeError("Value must be a list when updating a slice.")

            if len(value) != (stop - start):  # Enforce exact replacement
                raise ValueError(
                    "Replacement list must have the same length as the slice."
                )

            # Replace values item-by-item
            for i, val in enumerate(value):
                self.__setitem__(start + i, val)  # Recursive update for each index

        else:
            raise TypeError("Invalid index type. Must be int or slice.")

    def __delitem__(self, index: Union[int, slice]) -> None:
        """Delete an item or slice from the list."""
        if isinstance(index, int):
            if index < 0:
                index = len(self) + index

            if index < 0 or index >= len(self):
                raise IndexError("list index out of range")

            # For simplicity, convert to list, delete, then rebuild
            all_items = list(self)
            del all_items[index]

            # Rebuild the list
            self.clear()
            for item in all_items:
                self.append(item)

        elif isinstance(index, slice):
            # Convert to list, delete slice, then rebuild
            all_items = list(self)
            del all_items[index]

            # Rebuild the list
            self.clear()
            for item in all_items:
                self.append(item)
        else:
            raise TypeError("Invalid index type. Must be int or slice.")

    def combine_chunks(self) -> List[Dict[str, Any]]:
        """Loads and combines all chunks into a single list (if needed)."""
        combined_data = []
        for chunk_index in range(self.chunk_count):
            combined_data.extend(self._load_chunk(chunk_index))
        combined_data.extend(self._in_memory_list)  # Include in-memory items
        logging.info(f"Combined {self.chunk_count} chunks into a single list.")
        return combined_data

    def cleanup_chunks(self) -> None:
        """Deletes all stored chunk files from disk."""
        for chunk_index in range(self.chunk_count):
            chunk_file = os.path.join(
                self.disk_path, f"chunk_{self._file_identifier}_{chunk_index}.pkl"
            )
            try:
                if os.path.exists(chunk_file):
                    os.remove(chunk_file)
                    logging.debug(f"Deleted {chunk_file}")
            except OSError as e:
                # Only log as debug instead of error for temporary directory cleanup
                logging.debug(f"Could not delete {chunk_file}: {e}")
        self.chunk_count = 0  # Reset chunk tracking

    def serialize(self, max_workers: Optional[int] = None) -> None:
        """Serializes the list of dictionaries by converting certain types to
        JSON strings and updates the underlying files using multiple threads.
        """

        def process_chunk(chunk_index: int) -> None:
            chunk_data = self._load_chunk(chunk_index)
            for record in chunk_data:
                for key, value in record.items():
                    if isinstance(value, (bool, dict, list)):
                        record[key] = json.dumps(value)
            # Save the modified chunk back to disk
            chunk_file = os.path.join(
                self.disk_path, f"chunk_{self._file_identifier}_{chunk_index}.pkl"
            )
            with open(chunk_file, "wb") as f:
                pickle.dump(chunk_data, f)
            logging.info(f"Serialized and updated chunk {chunk_index} in {chunk_file}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(process_chunk, range(self.chunk_count))

        # Serialize remaining in-memory items
        for record in self._in_memory_list:
            for key, value in record.items():
                if isinstance(value, (bool, dict, list)):
                    record[key] = json.dumps(value)

    def map(
        self,
        func: Callable[[Dict[str, Any]], Dict[str, Any]],
        max_workers: Optional[int] = None,
    ) -> None:
        """Processes records in chunks using the provided function with multiple
        threads.

        Args:
            func (callable): Function to apply to each record in the chunk.
            max_workers (int, optional): The maximum number of threads to use.
                Defaults to None, which means the number of threads will be
                determined by the system.

        Returns:
            None (Modifies the records in-place)
        """

        def process_chunk(chunk_index: int) -> None:
            chunk_data = self._load_chunk(chunk_index)
            transformed_chunk = list(map(func, chunk_data))

            # Save the modified chunk back to disk
            chunk_file = os.path.join(
                self.disk_path, f"chunk_{self._file_identifier}_{chunk_index}.pkl"
            )
            with open(chunk_file, "wb") as f:
                pickle.dump(transformed_chunk, f)
            logging.info(
                f"Applied function to chunk {chunk_index} and updated {chunk_file}"
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(process_chunk, range(self.chunk_count))

        # Apply function to remaining in-memory items
        self._in_memory_list = list(map(func, self._in_memory_list))

    def __len__(self) -> int:
        """Returns the total number of items in the disk-backed list."""
        return self.chunk_count * self.chunk_size + len(self._in_memory_list)

    def __repr__(self) -> str:
        """Return a string representation of the PagedList."""
        return f"<PagedList: {len(self)} items across {self.chunk_count} chunks>"

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        if self.is_empty:
            return "PagedList(empty)"
        return f"PagedList({len(self)} items)"

    def __eq__(self, other: object) -> bool:
        """Check equality with another PagedList or list."""
        if isinstance(other, PagedList):
            if len(self) != len(other):
                return False
            return all(a == b for a, b in zip(self, other))
        elif isinstance(other, list):
            return list(self) == other
        return False

    def __ne__(self, other: object) -> bool:
        """Check inequality."""
        return not self.__eq__(other)

    def __list__(self) -> List[Dict[str, Any]]:
        return self.combine_chunks()

    def __enter__(self) -> "PagedList":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> Literal[False]:
        """Context manager exit with automatic cleanup."""
        self.cleanup_chunks()
        return False

    def clear(self) -> None:
        """Remove all items from the list."""
        self.cleanup_chunks()
        self._in_memory_list.clear()

    def insert(self, index: int, value: Dict[str, Any]) -> None:
        """Insert an item at a specific position."""
        if index < 0:
            index = max(0, len(self) + index)
        elif index > len(self):
            index = len(self)

        # For simplicity, convert to list, insert, then rebuild
        # This is not the most efficient for large lists, but it's correct
        all_items = list(self)
        all_items.insert(index, value)

        # Rebuild the list
        self.clear()
        for item in all_items:
            self.append(item)

    def remove(self, value: Dict[str, Any]) -> None:
        """Remove first occurrence of value."""
        for i, item in enumerate(self):
            if item == value:
                del self[i]
                return
        raise ValueError(f"{value} not in list")

    def pop(self, index: int = -1) -> Dict[str, Any]:
        """Remove and return item at index (default last)."""
        if len(self) == 0:
            raise IndexError("pop from empty list")

        if index < 0:
            index = len(self) + index

        if index < 0 or index >= len(self):
            raise IndexError("pop index out of range")

        value = self[index]
        if isinstance(value, list):
            raise TypeError("Cannot pop a slice")
        del self[index]
        return value

    def index(
        self, value: Dict[str, Any], start: int = 0, stop: Optional[int] = None
    ) -> int:
        """Return index of first occurrence of value."""
        if stop is None:
            stop = len(self)

        for i in range(start, min(stop, len(self))):
            if self[i] == value:
                return i
        raise ValueError(f"{value} not in list")

    def count(self, value: Dict[str, Any]) -> int:
        """Return number of occurrences of value."""
        return sum(1 for item in self if item == value)

    def copy(self) -> "PagedList":
        """Return a shallow copy of the list."""
        new_list = PagedList(chunk_size=self.chunk_size, disk_path=self.disk_path)
        new_list.extend(self)
        return new_list


def append_data(cl: PagedList, num_items: int) -> None:
    """Appends a specified number of items to the PagedList.

    Args:
        cl (PagedList): The PagedList instance to append data to.
        num_items (int): The number of items to append to the list.
    """
    for i in range(num_items):
        cl.append({"id": i, "value": i * 2})
    print(cl)  # Display object info


def example_usage() -> None:
    """Demonstrate the usage of PagedList."""
    # Create the disk-backed list
    cl = PagedList(chunk_size=50_000)

    # First appending phase
    num_items = 1_000_000
    batch_size = 1_000_010
    for i in range(0, num_items, batch_size):
        append_data(cl, batch_size)

    # Verify a single item retrieval
    print(cl[10_000])

    # Check the length of the list
    print(len(cl))

    # Grab a slice assumed to be between two chunks
    print(cl[49_999:50_001])

    # Update an item
    cl[10_000] = {"id": 10_000, "value": 42}

    # Show that the item is updated
    print(cl[10_000])

    # Test extending the list
    cl.extend([{"id": 10_001, "value": 43}, {"id": 10_002, "value": 44}])

    # show the updated length
    print(f"Length after extending: {len(cl)}")

    # Serialize the list
    # to test serialization lets edit values in the middle of the list
    cl[10_000] = {
        "id": 10_000,
        "value": 42,
        "new_value": "hello",
        "new_list": [1, 2, 3],
        "new_dict": {"a": 1, "b": 2},
        "new_bool": True,
    }
    cl.serialize()

    # Test to ensure no instance of list, bool, or dict within the values
    # from cl[9_000:11_000]
    for record in cl[9_000:11_000]:
        for value in record.values():  # type: ignore
            assert not isinstance(
                value, (list, bool, dict)
            ), f"Found instance of {type(value)} in record {record}"
    print("Serialization test passed")

    # Apply a function to all records
    def add_one(record: Dict[str, Any]) -> Dict[str, Any]:
        record["value"] += 1
        return record

    value_before = cl[10_500]["value"]  # type: ignore
    cl.map(add_one)
    value_after = cl[10_500]["value"]  # type: ignore
    # Verify the updated value
    assert (
        value_after == value_before + 1
    ), f"Expected {value_before + 1}, got {value_after}"

    print(
        f"The length of the list is {len(cl)} and the length of the list "
        f"converted to a list is {len(list(cl))}"
    )

    cl[10:12] = [
        {"id": 10, "value": 42, "new_value": "hello"},
        {"id": 11, "value": 99, "new_list": [1, 2, 3]},
    ]

    print(cl[10:12])  # Verify update

    # Cleanup disk
    cl.cleanup_chunks()
