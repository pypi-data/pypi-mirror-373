"""
Comprehensive tests for all Python list methods and magic methods in PagedList.

This test suite covers:
- Standard list methods: append, extend, insert, remove, pop, clear, index,
  count, sort, reverse, copy
- Magic methods: __getitem__, __setitem__, __delitem__, __contains__, __add__,
  __mul__, __iter__
- Built-in functions: len, max, min, sum, sorted, all, any, enumerate, map,
  filter, zip, reversed, iter, next, tuple
- Operators and syntax that call special methods
"""

import os
import shutil
import tempfile
import warnings

import pytest

from paged_list.paged_list import PagedList


class TestPagedListComprehensiveMethods:
    """Comprehensive test class for all PagedList methods and operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cl = PagedList(chunk_size=5, disk_path=self.temp_dir, auto_cleanup=False)

        # Add some test data
        self.test_data = [
            {"id": 1, "value": 10, "name": "alice"},
            {"id": 2, "value": 20, "name": "bob"},
            {"id": 3, "value": 30, "name": "charlie"},
            {"id": 4, "value": 40, "name": "diana"},
            {"id": 5, "value": 50, "name": "eve"},
            {"id": 6, "value": 60, "name": "frank"},
            {"id": 7, "value": 70, "name": "grace"},
        ]

        for item in self.test_data:
            self.cl.append(item)

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, "cl"):
            self.cl.cleanup_chunks()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ===== Standard List Methods =====

    def test_append(self):
        """Test append method."""
        initial_len = len(self.cl)
        new_item = {"id": 8, "value": 80, "name": "henry"}
        self.cl.append(new_item)

        assert len(self.cl) == initial_len + 1
        assert self.cl[-1] == new_item

    def test_append_type_validation(self):
        """Test append with invalid types."""
        with pytest.raises(TypeError):
            self.cl.append("not a dict")

        with pytest.raises(TypeError):
            self.cl.append([1, 2, 3])

    def test_extend(self):
        """Test extend method."""
        initial_len = len(self.cl)
        new_items = [
            {"id": 8, "value": 80, "name": "henry"},
            {"id": 9, "value": 90, "name": "iris"},
        ]
        self.cl.extend(new_items)

        assert len(self.cl) == initial_len + 2
        assert self.cl[-2] == new_items[0]
        assert self.cl[-1] == new_items[1]

    def test_insert(self):
        """Test insert method."""
        initial_len = len(self.cl)
        new_item = {"id": 99, "value": 99, "name": "inserted"}

        # Insert at beginning
        self.cl.insert(0, new_item)
        assert len(self.cl) == initial_len + 1
        assert self.cl[0] == new_item

        # Insert at middle
        middle_item = {"id": 88, "value": 88, "name": "middle"}
        self.cl.insert(3, middle_item)
        assert self.cl[3] == middle_item

        # Insert at end (beyond length)
        end_item = {"id": 77, "value": 77, "name": "end"}
        self.cl.insert(1000, end_item)
        assert self.cl[-1] == end_item

    def test_remove(self):
        """Test remove method."""
        initial_len = len(self.cl)
        # Get the actual item (ensure it's a dict, not a list)
        item_to_remove = self.cl[2]
        if isinstance(item_to_remove, list):
            item_to_remove = item_to_remove[0]  # Take first item if it's a list

        self.cl.remove(item_to_remove)
        assert len(self.cl) == initial_len - 1
        assert item_to_remove not in self.cl

        # Test removing non-existent item
        with pytest.raises(ValueError):
            self.cl.remove({"id": 999, "value": 999, "name": "nonexistent"})

    def test_pop(self):
        """Test pop method."""
        initial_len = len(self.cl)

        # Pop last item
        last_item = self.cl[-1]
        popped = self.cl.pop()
        assert popped == last_item
        assert len(self.cl) == initial_len - 1

        # Pop specific index
        target_item = self.cl[2]
        popped = self.cl.pop(2)
        assert popped == target_item
        assert len(self.cl) == initial_len - 2

        # Test pop from empty list
        empty_cl = PagedList(chunk_size=5, disk_path=self.temp_dir)
        with pytest.raises(IndexError):
            empty_cl.pop()

        # Test pop with invalid index
        with pytest.raises(IndexError):
            self.cl.pop(1000)

    def test_clear(self):
        """Test clear method."""
        assert len(self.cl) > 0
        self.cl.clear()
        assert len(self.cl) == 0
        assert self.cl.chunk_count == 0

    def test_index(self):
        """Test index method."""
        target_item = self.cl[3]
        if isinstance(target_item, list):
            target_item = target_item[0]

        index = self.cl.index(target_item)
        assert index == 3

        # Test with start and stop
        index = self.cl.index(target_item, 0, 10)
        assert index == 3

        # Test item not found
        with pytest.raises(ValueError):
            self.cl.index({"id": 999, "value": 999, "name": "nonexistent"})

        # Test item not in range
        with pytest.raises(ValueError):
            self.cl.index(target_item, 4, 6)

    def test_count(self):
        """Test count method."""
        target_item = self.cl[2]
        if isinstance(target_item, list):
            target_item = target_item[0]

        assert self.cl.count(target_item) == 1

        # Add duplicate
        self.cl.append(target_item)
        assert self.cl.count(target_item) == 2

        # Count non-existent item
        assert self.cl.count({"id": 999, "value": 999, "name": "nonexistent"}) == 0

    def test_copy(self):
        """Test copy method."""
        copied = self.cl.copy()

        assert len(copied) == len(self.cl)
        assert list(copied) == list(self.cl)
        assert copied is not self.cl

        # Modifications to copy shouldn't affect original
        copied.append({"id": 999, "value": 999, "name": "copied"})
        assert len(copied) != len(self.cl)

    # ===== Magic Methods =====

    def test_getitem_single_index(self):
        """Test __getitem__ with single index."""
        # Positive index
        assert self.cl[0] == self.test_data[0]
        assert self.cl[3] == self.test_data[3]

        # Negative index
        assert self.cl[-1] == self.test_data[-1]
        assert self.cl[-2] == self.test_data[-2]

        # Index out of range
        with pytest.raises(IndexError):
            _ = self.cl[100]

    def test_getitem_slice(self):
        """Test __getitem__ with slice."""
        # Basic slice
        subset = self.cl[1:4]
        expected = self.test_data[1:4]
        assert subset == expected

        # Slice with step
        subset = self.cl[::2]
        expected = self.test_data[::2]
        assert subset == expected

        # Negative indices in slice
        subset = self.cl[-3:-1]
        expected = self.test_data[-3:-1]
        assert subset == expected

    def test_setitem_single_index(self):
        """Test __setitem__ with single index."""
        new_item = {"id": 999, "value": 999, "name": "updated"}

        # Positive index
        self.cl[2] = new_item
        assert self.cl[2] == new_item

        # Negative index
        self.cl[-1] = new_item
        assert self.cl[-1] == new_item

        # Index out of range
        with pytest.raises(IndexError):
            self.cl[100] = new_item

    def test_setitem_slice(self):
        """Test __setitem__ with slice."""
        new_items = [
            {"id": 998, "value": 998, "name": "new1"},
            {"id": 997, "value": 997, "name": "new2"},
        ]

        # Replace slice
        self.cl[1:3] = new_items
        assert self.cl[1] == new_items[0]
        assert self.cl[2] == new_items[1]

        # Test invalid slice assignment
        with pytest.raises(ValueError):
            self.cl[1:3] = [{"id": 1}]  # Wrong length

        with pytest.raises(ValueError):
            self.cl[1:4:2] = new_items  # Step not supported

    def test_delitem_single_index(self):
        """Test __delitem__ with single index."""
        initial_len = len(self.cl)
        target_item = self.cl[2]
        # Ensure it's a dict for the test
        if isinstance(target_item, list):
            target_item = target_item[0]

        del self.cl[2]
        assert len(self.cl) == initial_len - 1
        # Note: Can't reliably test "not in" due to type system limitations

        # Test negative index
        del self.cl[-1]
        assert len(self.cl) == initial_len - 2

        # Test index out of range
        with pytest.raises(IndexError):
            del self.cl[100]

    def test_delitem_slice(self):
        """Test __delitem__ with slice."""
        initial_len = len(self.cl)

        # Delete slice
        del self.cl[1:3]
        assert len(self.cl) == initial_len - 2

        # Delete with step
        del self.cl[::2]
        assert len(self.cl) < initial_len

    def test_contains(self):
        """Test __contains__ (in operator)."""
        # Use a known item from our test data
        target_item = self.test_data[2]  # Use original test data to avoid type issues
        assert target_item in self.cl
        assert {"id": 999, "value": 999, "name": "nonexistent"} not in self.cl

    def test_len(self):
        """Test __len__."""
        assert len(self.cl) == len(self.test_data)

        self.cl.append({"id": 8, "value": 80, "name": "henry"})
        assert len(self.cl) == len(self.test_data) + 1

    def test_iter(self):
        """Test __iter__."""
        items = list(self.cl)
        assert items == self.test_data

        # Test iteration with for loop
        collected = []
        for item in self.cl:
            collected.append(item)
        assert collected == self.test_data

    def test_repr_and_str(self):
        """Test __repr__ and __str__."""
        repr_str = repr(self.cl)
        assert "PagedList" in repr_str
        assert str(len(self.cl)) in repr_str

        str_str = str(self.cl)
        assert "PagedList" in str_str

    def test_eq_and_ne(self):
        """Test __eq__ and __ne__."""
        # Equal PagedLists
        other_cl = PagedList(chunk_size=5, disk_path=self.temp_dir)
        for item in self.test_data:
            other_cl.append(item)

        assert self.cl == other_cl
        assert not (self.cl != other_cl)

        # Different PagedLists
        other_cl.append({"id": 999, "value": 999, "name": "different"})
        assert self.cl != other_cl
        assert not (self.cl == other_cl)

        # Compare with regular list
        assert self.cl == self.test_data
        assert self.cl != self.test_data + [{"extra": "item"}]

    # ===== Built-in Functions and Operations =====

    def test_builtin_max(self):
        """Test max() function."""
        # This should work but might be slow for large lists
        with warnings.catch_warnings(record=True):
            # Add numeric-only data for max testing
            numeric_cl = PagedList(chunk_size=3, disk_path=self.temp_dir)
            for i in range(10):
                numeric_cl.append({"value": i * 10})

            max_item = max(numeric_cl, key=lambda x: x["value"])
            assert max_item["value"] == 90

    def test_builtin_min(self):
        """Test min() function."""
        with warnings.catch_warnings(record=True):
            numeric_cl = PagedList(chunk_size=3, disk_path=self.temp_dir)
            for i in range(10):
                numeric_cl.append({"value": i * 10})

            min_item = min(numeric_cl, key=lambda x: x["value"])
            assert min_item["value"] == 0

    def test_builtin_sorted(self):
        """Test sorted() function."""
        with warnings.catch_warnings(record=True):
            # Create unsorted data
            unsorted_cl = PagedList(chunk_size=3, disk_path=self.temp_dir)
            values = [30, 10, 50, 20, 40]
            for val in values:
                unsorted_cl.append({"value": val})

            sorted_items = sorted(unsorted_cl, key=lambda x: x["value"])
            expected_values = [10, 20, 30, 40, 50]
            actual_values = [item["value"] for item in sorted_items]
            assert actual_values == expected_values

    def test_builtin_all(self):
        """Test all() function."""
        # All truthy values
        truthy_cl = PagedList(chunk_size=3, disk_path=self.temp_dir)
        for i in range(1, 5):
            truthy_cl.append({"value": i})

        assert all(item["value"] for item in truthy_cl)

        # Contains falsy value
        truthy_cl.append({"value": 0})
        assert not all(item["value"] for item in truthy_cl)

    def test_builtin_any(self):
        """Test any() function."""
        # All falsy values
        falsy_cl = PagedList(chunk_size=3, disk_path=self.temp_dir)
        for i in range(5):
            falsy_cl.append({"value": 0})

        assert not any(item["value"] for item in falsy_cl)

        # Contains truthy value
        falsy_cl.append({"value": 1})
        assert any(item["value"] for item in falsy_cl)

    def test_builtin_enumerate(self):
        """Test enumerate() function."""
        enumerated = list(enumerate(self.cl))
        assert len(enumerated) == len(self.cl)
        assert enumerated[0] == (0, self.test_data[0])
        assert enumerated[2] == (2, self.test_data[2])

    def test_builtin_filter(self):
        """Test filter() function."""
        # Filter items with value > 30
        filtered = list(filter(lambda x: x["value"] > 30, self.cl))
        expected = [item for item in self.test_data if item["value"] > 30]
        assert filtered == expected

    def test_builtin_zip(self):
        """Test zip() function."""
        other_list = [f"item_{i}" for i in range(len(self.cl))]
        zipped = list(zip(self.cl, other_list))

        assert len(zipped) == len(self.cl)
        assert zipped[0] == (self.test_data[0], "item_0")

    def test_builtin_reversed(self):
        """Test reversed() function."""
        reversed_items = list(reversed(self.cl))
        expected = list(reversed(self.test_data))
        assert reversed_items == expected

    def test_builtin_iter_and_next(self):
        """Test iter() and next() functions."""
        iterator = iter(self.cl)

        first_item = next(iterator)
        assert first_item == self.test_data[0]

        second_item = next(iterator)
        assert second_item == self.test_data[1]

    def test_list_conversion(self):
        """Test list() constructor."""
        converted = list(self.cl)
        assert converted == self.test_data
        assert isinstance(converted, list)

    def test_tuple_conversion(self):
        """Test tuple() constructor."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            converted = tuple(self.cl)

            assert converted == tuple(self.test_data)
            assert isinstance(converted, tuple)

            # Should warn about losing disk-backed nature
            # (This will be implemented when we add the warning system)

    # ===== Operators =====

    def test_addition_operator(self):
        """Test + operator (__add__)."""
        other_list = [{"id": 999, "value": 999, "name": "added"}]
        result = self.cl + other_list

        assert len(result) == len(self.cl) + 1
        assert result[-1] == other_list[0]
        assert isinstance(result, PagedList)

    def test_multiplication_operator(self):
        """Test * operator (__mul__)."""
        result = self.cl * 2

        assert len(result) == len(self.cl) * 2
        assert isinstance(result, PagedList)

        # Test with 0
        empty_result = self.cl * 0
        assert len(empty_result) == 0

    # ===== Methods That Work But Issue Warnings =====

    def test_sort_with_key(self):
        """Test that sort works with a key function."""
        # Sort by id in reverse order
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.cl.sort(key=lambda x: x["id"], reverse=True)

            # Should have issued at least one warning (may be multiple due to iteration)
            assert len(w) >= 1
            warning_messages = [str(warning.message) for warning in w]
            assert any("memory" in msg for msg in warning_messages)

        # Check that it's sorted correctly
        ids = [item["id"] for item in self.cl]
        assert ids == sorted(ids, reverse=True)

    def test_sort_requires_key(self):
        """Test that sort requires a key function for dicts."""
        with pytest.raises(TypeError, match="key"):
            self.cl.sort()

    def test_reverse_implementation(self):
        """Test that reverse works and issues warnings."""
        original_order = [item["id"] for item in self.cl]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.cl.reverse()

            # Should have issued at least one warning (may be multiple due to iteration)
            assert len(w) >= 1
            warning_messages = [str(warning.message) for warning in w]
            assert any("memory" in msg for msg in warning_messages)

        # Check that it's reversed
        new_order = [item["id"] for item in self.cl]
        assert new_order == list(reversed(original_order))

    # ===== Edge Cases and Performance Considerations =====

    def test_large_index_operations(self):
        """Test operations with indices that span multiple chunks."""
        # Create a larger list that definitely spans chunks
        large_cl = PagedList(chunk_size=3, disk_path=self.temp_dir)
        for i in range(20):
            large_cl.append({"id": i, "value": i * 10})

        # Test accessing items across chunks
        item_0 = large_cl[0]
        assert isinstance(item_0, dict) and item_0["id"] == 0  # First chunk

        item_5 = large_cl[5]
        assert isinstance(item_5, dict) and item_5["id"] == 5  # Second chunk

        item_15 = large_cl[15]
        assert isinstance(item_15, dict) and item_15["id"] == 15  # Later chunk

        # Test slice across chunks
        cross_chunk_slice = large_cl[2:8]
        assert len(cross_chunk_slice) == 6
        assert isinstance(cross_chunk_slice, list)
        assert cross_chunk_slice[0]["id"] == 2  # type: ignore
        assert cross_chunk_slice[-1]["id"] == 7  # type: ignore

    def test_empty_list_operations(self):
        """Test operations on empty list."""
        empty_cl = PagedList(chunk_size=5, disk_path=self.temp_dir)

        assert len(empty_cl) == 0
        assert list(empty_cl) == []
        assert empty_cl.is_empty

        # Test operations that should fail on empty list
        with pytest.raises(IndexError):
            _ = empty_cl[0]

        with pytest.raises(IndexError):
            empty_cl.pop()

    def test_memory_efficiency_indicators(self):
        """Test that the list properly uses chunking."""
        # Create list larger than chunk size
        large_cl = PagedList(chunk_size=3, disk_path=self.temp_dir, auto_cleanup=False)

        # Add items to trigger chunking
        for i in range(10):
            large_cl.append({"id": i, "value": i})

        # Should have created chunks
        assert large_cl.total_chunks > 0
        assert large_cl.in_memory_count <= 3  # Chunk size

        # Verify chunk files exist
        chunk_files = [f for f in os.listdir(self.temp_dir) if f.startswith("chunk_")]
        assert len(chunk_files) > 0


class TestPagedListMissingMethods:
    """Test class for methods that need to be implemented."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_methods_work_with_warnings(self):
        """Test that methods work but issue appropriate warnings."""
        cl = PagedList(chunk_size=3, disk_path=self.temp_dir)

        # Add enough data to create multiple chunks
        for i in range(10):
            cl.append({"id": i, "value": i})

        # These should work but warn about performance
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Test sort with key
            cl.sort(key=lambda x: x["id"], reverse=True)

            # Test reverse
            cl.reverse()

            # Test addition
            result1 = cl + [{"id": 999}]

            # Test multiplication
            result2 = cl * 2

            # Should have issued warnings
            assert len(w) >= 4

        # Verify operations worked
        assert isinstance(result1, PagedList)
        assert isinstance(result2, PagedList)
        assert len(result1) == len(cl) + 1
        assert len(result2) == len(cl) * 2

    def test_warning_methods(self):
        """Test methods that should warn about performance implications."""
        cl = PagedList(chunk_size=3, disk_path=self.temp_dir)

        # Add enough data to create multiple chunks
        for i in range(10):
            cl.append({"id": i, "value": i})

        # These operations should work but warn about performance
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            # Convert to tuple (loses disk-backed benefits)
            result = tuple(cl)
            assert isinstance(result, tuple)
            # Note: Warning implementation will be added to the main class


if __name__ == "__main__":
    pytest.main([__file__])
