"""Tests for the new Pythonic methods added to PagedList."""

import os
import shutil
import tempfile

import pytest

from paged_list.paged_list import PagedList


class TestPagedListPythonic:
    """Test class for new Pythonic methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cl = PagedList(chunk_size=3, disk_path=self.temp_dir, auto_cleanup=False)

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, "cl"):
            self.cl.cleanup_chunks()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_context_manager(self):
        """Test context manager functionality."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Test successful context manager usage
            with PagedList(chunk_size=2, disk_path=temp_dir, auto_cleanup=False) as cl:
                cl.append({"id": 1, "value": "test"})
                cl.append({"id": 2, "value": "test2"})
                cl.append({"id": 3, "value": "test3"})  # This should create a chunk
                assert len(cl) == 3
                assert cl.total_chunks == 1

            # After context, chunks should be cleaned up
            chunk_files = [f for f in os.listdir(temp_dir) if f.startswith("chunk_")]
            assert len(chunk_files) == 0

            # Test exception handling in context manager
            try:
                with PagedList(
                    chunk_size=2, disk_path=temp_dir, auto_cleanup=False
                ) as cl:
                    cl.append({"id": 1, "value": "test"})
                    raise ValueError("Test exception")
            except ValueError:
                pass

            # Chunks should still be cleaned up even after exception
            chunk_files = [f for f in os.listdir(temp_dir) if f.startswith("chunk_")]
            assert len(chunk_files) == 0

        finally:
            shutil.rmtree(temp_dir)

    def test_properties(self):
        """Test property methods."""
        # Test empty list properties
        assert self.cl.is_empty is True
        assert self.cl.total_chunks == 0
        assert self.cl.in_memory_count == 0

        # Add items and test properties
        self.cl.append({"id": 1, "value": "test"})
        self.cl.append({"id": 2, "value": "test2"})

        assert self.cl.is_empty is False
        assert self.cl.total_chunks == 0  # Still in memory
        assert self.cl.in_memory_count == 2

        # Force chunking
        self.cl.append({"id": 3, "value": "test3"})  # This should create a chunk
        self.cl.append({"id": 4, "value": "test4"})

        assert self.cl.total_chunks == 1
        assert self.cl.in_memory_count == 1

    def test_contains(self):
        """Test __contains__ method."""
        test_item = {"id": 1, "value": "test"}
        other_item = {"id": 2, "value": "other"}

        # Test empty list
        assert test_item not in self.cl

        # Add items
        self.cl.append(test_item)
        self.cl.append(other_item)

        # Test containment
        assert test_item in self.cl
        assert other_item in self.cl
        assert {"id": 3, "value": "nonexistent"} not in self.cl

        # Test with chunked data
        for i in range(5):
            self.cl.append({"id": i + 10, "value": f"chunk_test_{i}"})

        chunk_item = {"id": 12, "value": "chunk_test_2"}
        assert chunk_item in self.cl

    def test_clear(self):
        """Test clear method."""
        # Add items to create chunks
        for i in range(10):
            self.cl.append({"id": i, "value": f"test_{i}"})

        assert len(self.cl) == 10
        assert self.cl.total_chunks > 0

        # Clear the list
        self.cl.clear()

        assert len(self.cl) == 0
        assert self.cl.is_empty is True
        assert self.cl.total_chunks == 0
        assert self.cl.in_memory_count == 0

    def test_insert(self):
        """Test insert method."""
        # Test insert into empty list
        self.cl.insert(0, {"id": 1, "value": "first"})
        assert len(self.cl) == 1
        assert self.cl[0] == {"id": 1, "value": "first"}

        # Test insert at beginning
        self.cl.insert(0, {"id": 0, "value": "new_first"})
        assert len(self.cl) == 2
        assert self.cl[0] == {"id": 0, "value": "new_first"}
        assert self.cl[1] == {"id": 1, "value": "first"}

        # Test insert at end
        self.cl.insert(2, {"id": 2, "value": "last"})
        assert len(self.cl) == 3
        assert self.cl[2] == {"id": 2, "value": "last"}

        # Test insert in middle
        self.cl.insert(1, {"id": 0.5, "value": "middle"})
        assert len(self.cl) == 4
        assert self.cl[1] == {"id": 0.5, "value": "middle"}

        # Test insert with negative index
        self.cl.insert(-1, {"id": -1, "value": "near_end"})
        assert self.cl[-2] == {"id": -1, "value": "near_end"}

        # Test insert beyond end
        self.cl.insert(100, {"id": 100, "value": "beyond_end"})
        assert self.cl[-1] == {"id": 100, "value": "beyond_end"}

    def test_remove(self):
        """Test remove method."""
        # Add test items
        item1 = {"id": 1, "value": "test1"}
        item2 = {"id": 2, "value": "test2"}
        item3 = {"id": 3, "value": "test3"}

        self.cl.extend([item1, item2, item3, item1])  # Add duplicate

        # Test remove first occurrence
        self.cl.remove(item1)
        assert len(self.cl) == 3
        assert self.cl[0] == item2
        assert item1 in self.cl  # Duplicate still exists

        # Test remove from middle
        self.cl.remove(item2)
        assert len(self.cl) == 2
        assert item2 not in self.cl

        # Test remove non-existent item
        with pytest.raises(ValueError, match="not in list"):
            self.cl.remove({"id": 999, "value": "nonexistent"})

    def test_pop(self):
        """Test pop method."""
        # Test pop from empty list
        with pytest.raises(IndexError, match="pop from empty list"):
            self.cl.pop()

        # Add test items
        items = [{"id": i, "value": f"test_{i}"} for i in range(5)]
        self.cl.extend(items)

        # Test pop from end (default)
        popped = self.cl.pop()
        assert popped == {"id": 4, "value": "test_4"}
        assert len(self.cl) == 4

        # Test pop from beginning
        popped = self.cl.pop(0)
        assert popped == {"id": 0, "value": "test_0"}
        assert len(self.cl) == 3

        # Test pop from middle
        popped = self.cl.pop(1)
        assert popped == {"id": 2, "value": "test_2"}
        assert len(self.cl) == 2

        # Test pop with negative index
        popped = self.cl.pop(-1)
        assert popped == {"id": 3, "value": "test_3"}
        assert len(self.cl) == 1

        # Test pop out of range
        with pytest.raises(IndexError, match="pop index out of range"):
            self.cl.pop(10)

        with pytest.raises(IndexError, match="pop index out of range"):
            self.cl.pop(-10)

    def test_index(self):
        """Test index method."""
        # Add test items
        items = [
            {"id": 1, "value": "test1"},
            {"id": 2, "value": "test2"},
            {"id": 3, "value": "test3"},
            {"id": 2, "value": "test2"},  # Duplicate
            {"id": 4, "value": "test4"},
        ]
        self.cl.extend(items)

        # Test finding first occurrence
        assert self.cl.index({"id": 2, "value": "test2"}) == 1

        # Test finding with start parameter
        assert self.cl.index({"id": 2, "value": "test2"}, start=2) == 3

        # Test finding with start and stop parameters
        assert self.cl.index({"id": 2, "value": "test2"}, start=0, stop=2) == 1

        # Test item not found
        with pytest.raises(ValueError, match="not in list"):
            self.cl.index({"id": 999, "value": "nonexistent"})

        # Test item not found in range
        with pytest.raises(ValueError, match="not in list"):
            self.cl.index({"id": 4, "value": "test4"}, start=0, stop=3)

    def test_count(self):
        """Test count method."""
        # Test count in empty list
        assert self.cl.count({"id": 1, "value": "test"}) == 0

        # Add test items with duplicates
        items = [
            {"id": 1, "value": "test1"},
            {"id": 2, "value": "test2"},
            {"id": 1, "value": "test1"},  # Duplicate
            {"id": 3, "value": "test3"},
            {"id": 1, "value": "test1"},  # Another duplicate
        ]
        self.cl.extend(items)

        # Test counting
        assert self.cl.count({"id": 1, "value": "test1"}) == 3
        assert self.cl.count({"id": 2, "value": "test2"}) == 1
        assert self.cl.count({"id": 3, "value": "test3"}) == 1
        assert self.cl.count({"id": 999, "value": "nonexistent"}) == 0

    def test_copy(self):
        """Test copy method."""
        # Add test items
        items = [{"id": i, "value": f"test_{i}"} for i in range(8)]
        self.cl.extend(items)

        # Create copy
        cl_copy = self.cl.copy()

        # Test copy properties
        assert len(cl_copy) == len(self.cl)
        assert cl_copy == self.cl
        assert cl_copy is not self.cl
        assert cl_copy.chunk_size == self.cl.chunk_size
        assert cl_copy.disk_path == self.cl.disk_path

        # Test independence
        cl_copy.append({"id": 999, "value": "copy_only"})
        assert len(cl_copy) == len(self.cl) + 1
        assert {"id": 999, "value": "copy_only"} not in self.cl

        # Clean up copy
        cl_copy.cleanup_chunks()

    def test_delitem(self):
        """Test __delitem__ method."""
        # Add test items
        items = [{"id": i, "value": f"test_{i}"} for i in range(7)]
        self.cl.extend(items)

        # Test delete single item
        original_len = len(self.cl)
        del self.cl[0]
        assert len(self.cl) == original_len - 1
        assert self.cl[0] == {"id": 1, "value": "test_1"}

        # Test delete with negative index
        del self.cl[-1]
        assert len(self.cl) == original_len - 2
        assert self.cl[-1] == {"id": 5, "value": "test_5"}

        # Test delete slice
        del self.cl[1:3]
        assert len(self.cl) == original_len - 4

        # Test delete out of range
        with pytest.raises(IndexError, match="list index out of range"):
            del self.cl[100]

    def test_equality(self):
        """Test __eq__ and __ne__ methods."""
        # Create two identical lists
        items = [{"id": i, "value": f"test_{i}"} for i in range(5)]

        cl1 = PagedList(
            chunk_size=3, disk_path=self.temp_dir + "_1", auto_cleanup=False
        )
        cl2 = PagedList(
            chunk_size=3, disk_path=self.temp_dir + "_2", auto_cleanup=False
        )

        try:
            # Test empty lists
            assert cl1 == cl2
            assert not (cl1 != cl2)

            # Add same items
            cl1.extend(items)
            cl2.extend(items)

            assert cl1 == cl2
            assert not (cl1 != cl2)

            # Test equality with regular list
            assert cl1 == items
            assert cl2 == items

            # Test inequality
            cl2.append({"id": 999, "value": "extra"})
            assert cl1 != cl2
            assert not (cl1 == cl2)

            # Test inequality with different types
            assert cl1 != "not a list"
            assert cl1 != 123

        finally:
            cl1.cleanup_chunks()
            cl2.cleanup_chunks()

    def test_str_and_repr(self):
        """Test string representations."""
        # Test empty list
        assert str(self.cl) == "PagedList(empty)"
        assert "PagedList:" in repr(self.cl)
        assert "0 items" in repr(self.cl)

        # Test non-empty list
        self.cl.append({"id": 1, "value": "test"})
        assert str(self.cl) == "PagedList(1 items)"
        assert "1 items" in repr(self.cl)

    def test_type_checking(self):
        """Test enhanced type checking."""
        # Test append with wrong type
        with pytest.raises(TypeError, match="Expected dict, got str"):
            self.cl.append("not a dict")

        with pytest.raises(TypeError, match="Expected dict, got list"):
            self.cl.append([1, 2, 3])

        with pytest.raises(TypeError, match="Expected dict, got int"):
            self.cl.append(123)

    def test_configuration_validation(self):
        """Test constructor parameter validation."""
        # Test invalid chunk_size
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            PagedList(chunk_size=0)

        with pytest.raises(ValueError, match="chunk_size must be positive"):
            PagedList(chunk_size=-1)

        # Test valid configurations
        cl = PagedList(chunk_size=1, disk_path="test", auto_cleanup=False)
        assert cl.chunk_size == 1
        assert cl.disk_path == "test"
        assert cl._auto_cleanup is False
        cl.cleanup_chunks()

    def test_chunked_operations(self):
        """Test new methods work correctly with chunked data."""
        # Create data that will span multiple chunks
        items = [{"id": i, "value": f"test_{i}"} for i in range(10)]
        self.cl.extend(items)

        # Verify chunking occurred
        assert self.cl.total_chunks > 1

        # Test operations across chunks
        assert {"id": 5, "value": "test_5"} in self.cl
        assert self.cl.count({"id": 5, "value": "test_5"}) == 1
        assert self.cl.index({"id": 5, "value": "test_5"}) == 5

        # Test remove across chunks
        self.cl.remove({"id": 5, "value": "test_5"})
        assert len(self.cl) == 9
        assert {"id": 5, "value": "test_5"} not in self.cl

        # Test pop across chunks - after removing id=5, the item at index 4 is now id=4
        popped = self.cl.pop(4)
        assert popped == {"id": 4, "value": "test_4"}

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test insert at negative index beyond list length
        self.cl.insert(-100, {"id": -100, "value": "far_negative"})
        assert self.cl[0] == {"id": -100, "value": "far_negative"}

        # Test operations on single item
        self.cl.clear()
        self.cl.append({"id": 1, "value": "single"})

        assert self.cl.count({"id": 1, "value": "single"}) == 1
        assert self.cl.index({"id": 1, "value": "single"}) == 0

        popped = self.cl.pop()
        assert popped == {"id": 1, "value": "single"}
        assert self.cl.is_empty


class TestPagedListPythonicIntegration:
    """Integration tests for Pythonic methods."""

    def test_method_chaining_simulation(self):
        """Test using multiple methods together."""
        temp_dir = tempfile.mkdtemp()
        try:
            with PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False) as cl:
                # Build a list
                items = [{"id": i, "value": f"test_{i}"} for i in range(8)]
                cl.extend(items)

                # Manipulate it
                cl.insert(0, {"id": -1, "value": "inserted"})
                cl.remove({"id": 3, "value": "test_3"})
                last_item = cl.pop()

                # Verify final state
                assert len(cl) == 7
                assert cl[0] == {"id": -1, "value": "inserted"}
                assert {"id": 3, "value": "test_3"} not in cl
                assert last_item == {"id": 7, "value": "test_7"}

                # Test copy and equality
                cl_copy = cl.copy()
                assert cl == cl_copy

                cl_copy.cleanup_chunks()

        finally:
            shutil.rmtree(temp_dir)

    def test_compatibility_with_existing_methods(self):
        """Test that new methods work with existing functionality."""
        temp_dir = tempfile.mkdtemp()
        try:
            cl = PagedList(chunk_size=2, disk_path=temp_dir, auto_cleanup=False)

            # Mix old and new methods
            cl.append({"id": 1, "value": "old_method"})
            cl.insert(0, {"id": 0, "value": "new_method"})

            # Test slicing still works
            slice_result = cl[0:2]
            assert len(slice_result) == 2

            # Test serialization still works
            cl.append({"id": 2, "data": [1, 2, 3], "flag": True})
            cl.serialize()

            # Test map still works
            def add_processed_flag(record):
                record["processed"] = True
                return record

            cl.map(add_processed_flag)

            # Verify all items have the processed flag
            for item in cl:
                assert item.get("processed") is True

            cl.cleanup_chunks()

        finally:
            shutil.rmtree(temp_dir)
