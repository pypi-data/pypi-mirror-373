#!/usr/bin/env python3
"""Test script to demonstrate the new Pythonic features of PagedList."""

import os
import sys

from paged_list.paged_list import PagedList

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_pythonic_features():
    """Test the new Pythonic features."""

    # Test context manager
    print("Testing context manager...")
    with PagedList(chunk_size=5) as cl:
        cl.append({"id": 1, "name": "Alice"})
        cl.append({"id": 2, "name": "Bob"})
        cl.append({"id": 3, "name": "Charlie"})
        print(f"Created list with {len(cl)} items")
        print(f"String representation: {str(cl)}")
        print(f"Repr: {repr(cl)}")
    # Chunks should be automatically cleaned up here

    # Test new list methods
    print("\nTesting new list methods...")
    cl = PagedList(chunk_size=3)

    # Test append with type checking
    cl.append({"id": 1, "value": "test"})
    cl.append({"id": 2, "value": "hello"})
    cl.append({"id": 3, "value": "world"})

    print(f"Initial list: {len(cl)} items")

    # Test properties
    print(f"Is empty: {cl.is_empty}")
    print(f"Total chunks: {cl.total_chunks}")
    print(f"In memory count: {cl.in_memory_count}")

    # Test contains
    test_item = {"id": 2, "value": "hello"}
    print(f"Contains {test_item}: {test_item in cl}")

    # Test insert
    cl.insert(1, {"id": 1.5, "value": "inserted"})
    print(f"After insert: {len(cl)} items")

    # Test pop
    popped = cl.pop()
    print(f"Popped: {popped}")
    print(f"After pop: {len(cl)} items")

    # Test index
    try:
        idx = cl.index({"id": 1, "value": "test"})
        print(f"Index of first item: {idx}")
    except ValueError as e:
        print(f"Index error: {e}")

    # Test count
    cl.append({"id": 1, "value": "test"})  # Add duplicate
    count = cl.count({"id": 1, "value": "test"})
    print(f"Count of first item: {count}")

    # Test copy
    cl_copy = cl.copy()
    print(f"Copy has {len(cl_copy)} items")

    # Test equality
    print(f"Original equals copy: {cl == cl_copy}")

    # Test clear
    cl.clear()
    print(f"After clear: {len(cl)} items")
    print(f"Is empty: {cl.is_empty}")

    # Test error handling
    print("\nTesting error handling...")
    try:
        cl.append("not a dict")  # Should raise TypeError
    except TypeError as e:
        print(f"Caught expected error: {e}")

    try:
        cl.remove({"nonexistent": "item"})  # Should raise ValueError
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Clean up
    cl_copy.cleanup_chunks()
    print("\nAll tests completed!")


if __name__ == "__main__":
    test_pythonic_features()
