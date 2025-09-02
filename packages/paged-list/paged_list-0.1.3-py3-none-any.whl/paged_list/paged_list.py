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
import warnings
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
        """Iterate over all items in the list."""
        # Warn if multiple chunks exist (indicates large dataset being loaded)
        if self.chunk_count > 0:
            warnings.warn(
                "Iterating over PagedList with disk-backed chunks loads all "
                "data into memory. This may be slow and memory-intensive for "
                "large lists.",
                UserWarning,
                stacklevel=2,
            )

        for i in range(len(self)):
            yield self[i]  # type: ignore

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

    def sort(
        self,
        *,
        key: Optional[Callable[[Dict[str, Any]], Any]] = None,
        reverse: bool = False,
    ) -> None:
        """Sort the list in place.

        Warning: This operation loads all data into memory and may be slow for large lists.
        Note: A key function is required when sorting dictionaries.
        """
        if self.chunk_count > 0:
            warnings.warn(
                "Sorting a PagedList with multiple chunks loads all data "
                "into memory. This may be slow and memory-intensive for "
                "large lists.",
                UserWarning,
                stacklevel=2,
            )

        if key is None:
            raise TypeError(
                "sort() missing required argument: 'key' (dictionaries "
                "require a key function)"
            )

        # Load all data, sort it, then rebuild the list
        all_items = list(self)
        all_items.sort(key=key, reverse=reverse)

        # Rebuild the list
        self.clear()
        for item in all_items:
            self.append(item)

    def reverse(self) -> None:
        """Reverse the list in place.

        Warning: This operation loads all data into memory and may be slow for large lists.
        """
        if self.chunk_count > 0:
            warnings.warn(
                "Reversing a PagedList with multiple chunks loads all data "
                "into memory. This may be slow and memory-intensive for "
                "large lists.",
                UserWarning,
                stacklevel=2,
            )

        # Load all data, reverse it, then rebuild the list
        all_items = list(self)
        all_items.reverse()

        # Rebuild the list
        self.clear()
        for item in all_items:
            self.append(item)

    def __add__(self, other: Union[List[Dict[str, Any]], "PagedList"]) -> "PagedList":
        """Concatenate with another list or PagedList."""
        if self.chunk_count > 0:
            warnings.warn(
                "Adding lists with a multi-chunk PagedList loads all data into memory. "
                "Consider using extend() for better memory efficiency.",
                UserWarning,
                stacklevel=2,
            )

        new_list = self.copy()
        if isinstance(other, PagedList):
            new_list.extend(other)
        elif isinstance(other, list):
            new_list.extend(other)
        else:
            raise TypeError(f"Cannot concatenate PagedList with {type(other)}")
        return new_list

    def __mul__(self, other: int) -> "PagedList":
        """Repeat the list."""
        if not isinstance(other, int):
            raise TypeError(f"Cannot multiply PagedList by {type(other)}")

        if other < 0:
            other = 0

        if self.chunk_count > 0 and other > 1:
            warnings.warn(
                "Multiplying a multi-chunk PagedList loads all data into memory. "
                "This may be slow and memory-intensive for large lists.",
                UserWarning,
                stacklevel=2,
            )

        new_list = PagedList(chunk_size=self.chunk_size, disk_path=self.disk_path)
        for _ in range(other):
            new_list.extend(self)
        return new_list

    def __rmul__(self, other: int) -> "PagedList":
        """Repeat the list (reverse multiplication)."""
        return self.__mul__(other)

    def __reversed__(self) -> Iterator[Dict[str, Any]]:
        """Return a reverse iterator."""
        if self.chunk_count > 0:
            warnings.warn(
                "Creating a reverse iterator for a multi-chunk PagedList "
                "loads all data into memory. This may be slow and "
                "memory-intensive for large lists.",
                UserWarning,
                stacklevel=2,
            )

        # For efficiency, we'll load all data and reverse it
        all_items = list(self)
        return reversed(all_items)

    def __list__(self) -> List[Dict[str, Any]]:
        """Convert to a regular list with warning if chunked."""
        if self.chunk_count > 0:
            warnings.warn(
                "Converting a multi-chunk PagedList to list loads all data "
                "into memory and loses the disk-backed storage benefits. "
                "Consider iterating directly over the PagedList instead.",
                UserWarning,
                stacklevel=2,
            )
        return self.combine_chunks()

    def __tuple__(self) -> tuple:
        """Convert to tuple with warning."""
        if self.chunk_count > 0:
            warnings.warn(
                "Converting a multi-chunk PagedList to tuple loads all data "
                "into memory and loses the disk-backed storage benefits.",
                UserWarning,
                stacklevel=2,
            )
        return tuple(self.combine_chunks())
