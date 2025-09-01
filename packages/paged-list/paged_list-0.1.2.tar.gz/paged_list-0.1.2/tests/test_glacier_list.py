"""
Comprehensive tests for PagedList functionality.
"""

import json
import tempfile

from paged_list.paged_list import PagedList


def test_paged_list_initialization():
    """Test PagedList initialization with different parameters."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=1000, disk_path=temp_dir, auto_cleanup=False)
        assert cl.chunk_size == 1000
        assert cl.disk_path == temp_dir
        assert cl.is_empty
        cl.cleanup_chunks()


def test_paged_list_append_and_length():
    """Test appending items and length calculation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False)

        # Test empty list
        assert len(cl) == 0
        assert cl.is_empty

        # Add items
        for i in range(5):
            cl.append({"id": i, "value": f"item_{i}"})

        assert len(cl) == 5
        assert not cl.is_empty
        assert cl.chunk_count == 1  # Should have created one chunk
        assert cl.in_memory_count == 2  # 2 items remaining in memory

        cl.cleanup_chunks()


def test_paged_list_indexing():
    """Test indexing and slicing operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False)

        # Add test data
        test_data = [{"id": i, "value": f"item_{i}"} for i in range(7)]
        cl.extend(test_data)

        # Test positive indexing
        assert cl[0] == {"id": 0, "value": "item_0"}
        assert cl[3] == {"id": 3, "value": "item_3"}
        assert cl[6] == {"id": 6, "value": "item_6"}

        # Test negative indexing
        assert cl[-1] == {"id": 6, "value": "item_6"}
        assert cl[-7] == {"id": 0, "value": "item_0"}

        # Test slicing
        slice_result = cl[1:4]
        assert len(slice_result) == 3
        expected = [
            {"id": 1, "value": "item_1"},
            {"id": 2, "value": "item_2"},
            {"id": 3, "value": "item_3"},
        ]
        assert slice_result == expected

        cl.cleanup_chunks()


def test_paged_list_setitem():
    """Test item assignment."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False)

        # Add test data
        for i in range(5):
            cl.append({"id": i, "value": f"item_{i}"})

        # Test updating items
        cl[0] = {"id": 0, "value": "updated_item_0"}
        assert cl[0] == {"id": 0, "value": "updated_item_0"}

        cl[4] = {"id": 4, "value": "updated_item_4"}
        assert cl[4] == {"id": 4, "value": "updated_item_4"}

        cl.cleanup_chunks()


def test_paged_list_iteration():
    """Test iteration over the list."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False)

        # Add test data
        test_data = [{"id": i, "value": f"item_{i}"} for i in range(7)]
        cl.extend(test_data)

        # Test iteration
        collected = list(cl)
        assert len(collected) == 7
        assert collected == test_data

        # Test iteration with for loop
        collected_for = []
        for item in cl:
            collected_for.append(item)
        assert collected_for == test_data

        cl.cleanup_chunks()


def test_paged_list_contains():
    """Test 'in' operator."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False)

        test_item = {"id": 5, "value": "item_5"}
        missing_item = {"id": 99, "value": "missing"}

        # Add test data
        for i in range(10):
            cl.append({"id": i, "value": f"item_{i}"})

        assert test_item in cl
        assert missing_item not in cl

        cl.cleanup_chunks()


def test_paged_list_serialization():
    """Test serialization functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=2, disk_path=temp_dir, auto_cleanup=False)

        # Add data with various types
        test_data = [
            {
                "id": 0,
                "bool_val": True,
                "list_val": [1, 2, 3],
                "dict_val": {"nested": "value"},
            },
            {
                "id": 1,
                "bool_val": False,
                "list_val": [4, 5, 6],
                "dict_val": {"other": "data"},
            },
            {"id": 2, "bool_val": True, "simple": "string"},
        ]

        cl.extend(test_data)

        # Serialize
        cl.serialize()

        # Check that complex types are now JSON strings
        for item in cl:
            for key, value in item.items():
                if key in ["bool_val", "list_val", "dict_val"]:
                    assert isinstance(value, str)
                    # Verify it's valid JSON
                    parsed = json.loads(value)
                    assert parsed is not None

        cl.cleanup_chunks()


def test_paged_list_map():
    """Test map functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=2, disk_path=temp_dir, auto_cleanup=False)

        # Add test data
        for i in range(5):
            cl.append({"id": i, "value": i * 10})

        # Define transformation function
        def double_value(record):
            record = record.copy()  # Don't modify original
            record["value"] *= 2
            return record

        original_values = [item["value"] for item in cl]

        # Apply map
        cl.map(double_value)

        # Check results
        new_values = [item["value"] for item in cl]
        expected_values = [v * 2 for v in original_values]
        assert new_values == expected_values

        cl.cleanup_chunks()


def test_paged_list_operations():
    """Test list-like operations (insert, remove, pop, etc.)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False)

        # Test insert
        cl.append({"id": 0})
        cl.append({"id": 2})
        cl.insert(1, {"id": 1})

        assert cl[0] == {"id": 0}
        assert cl[1] == {"id": 1}
        assert cl[2] == {"id": 2}

        # Test remove
        cl.remove({"id": 1})
        assert len(cl) == 2
        assert cl[1] == {"id": 2}

        # Test pop
        popped = cl.pop()
        assert popped == {"id": 2}
        assert len(cl) == 1

        # Test clear
        cl.clear()
        assert len(cl) == 0
        assert cl.is_empty

        cl.cleanup_chunks()


def test_paged_list_copy():
    """Test copying functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=2, disk_path=temp_dir, auto_cleanup=False)

        # Add test data
        test_data = [{"id": i, "value": f"item_{i}"} for i in range(5)]
        cl.extend(test_data)

        # Create copy
        cl_copy = cl.copy()

        # Verify copy has same data
        assert len(cl_copy) == len(cl)
        assert list(cl_copy) == list(cl)

        # Verify they're independent
        cl.append({"id": 999, "value": "new_item"})
        assert len(cl_copy) != len(cl)

        cl.cleanup_chunks()
        cl_copy.cleanup_chunks()


def test_paged_list_error_handling():
    """Test error handling."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False)

        # Test invalid chunk_size
        try:
            PagedList(chunk_size=0)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

        # Test invalid data type
        try:
            cl.append("not a dict")
            assert False, "Should have raised TypeError"
        except TypeError:
            pass

        # Test index out of range
        try:
            _ = cl[0]  # Empty list
            assert False, "Should have raised IndexError"
        except IndexError:
            pass

        cl.cleanup_chunks()
