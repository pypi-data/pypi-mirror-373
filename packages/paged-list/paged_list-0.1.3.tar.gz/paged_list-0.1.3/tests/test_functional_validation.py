"""
Test file to validate that all implemented list methods and operators work correctly.

This is a validation test to ensure all the features we implemented actually function
as expected in real-world usage scenarios.
"""

import os
import shutil
import tempfile
import warnings

import pytest

from paged_list.paged_list import PagedList


class TestPagedListFunctionalValidation:
    """Functional validation tests for all PagedList methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_list_api_compatibility(self):
        """Test that PagedList works as a drop-in replacement for list."""
        # Create a PagedList that will span multiple chunks
        pl = PagedList(chunk_size=5, disk_path=self.temp_dir)

        # Also create a regular list for comparison
        regular_list = []

        # Test all append operations
        test_data = [{"id": i, "name": f"user_{i}", "score": i * 10} for i in range(15)]

        for item in test_data:
            pl.append(item)
            regular_list.append(item)

        # Test length
        assert len(pl) == len(regular_list)

        # Test indexing (positive and negative)
        assert pl[0] == regular_list[0]
        assert pl[7] == regular_list[7]
        assert pl[-1] == regular_list[-1]
        assert pl[-3] == regular_list[-3]

        # Test slicing
        assert pl[2:8] == regular_list[2:8]
        assert pl[::2] == regular_list[::2]
        assert pl[-5:-1] == regular_list[-5:-1]

        # Test iteration
        pl_items = list(pl)
        assert pl_items == regular_list

        # Test contains
        assert test_data[5] in pl
        assert {"id": 999, "name": "fake"} not in pl

        # Test equality
        assert pl == regular_list

        # Test copy
        pl_copy = pl.copy()
        assert pl_copy == pl
        assert pl_copy is not pl

    def test_list_modification_operations(self):
        """Test all list modification operations."""
        pl = PagedList(chunk_size=3, disk_path=self.temp_dir)

        # Start with some data
        initial_data = [{"id": i, "value": i * 2} for i in range(10)]
        pl.extend(initial_data)

        # Test insert
        new_item = {"id": 99, "value": 198}
        pl.insert(5, new_item)
        assert pl[5] == new_item
        assert len(pl) == 11

        # Test item assignment
        replacement_item = {"id": 88, "value": 176}
        pl[3] = replacement_item
        assert pl[3] == replacement_item

        # Test slice assignment
        new_slice = [{"id": 77, "value": 154}, {"id": 66, "value": 132}]
        pl[1:3] = new_slice
        assert pl[1:3] == new_slice

        # Test remove
        item_to_remove = pl[7]
        pl.remove(item_to_remove)
        assert item_to_remove not in pl

        # Test pop
        last_item = pl[-1]
        popped = pl.pop()
        assert popped == last_item

        specific_item = pl[2]
        popped_specific = pl.pop(2)
        assert popped_specific == specific_item

        # Test del
        target_item = pl[4]
        del pl[4]
        assert target_item not in pl

    def test_advanced_operations_with_warnings(self):
        """Test operations that should work but issue performance warnings."""
        pl = PagedList(chunk_size=3, disk_path=self.temp_dir)

        # Add enough data to create multiple chunks
        for i in range(12):
            pl.append({"id": i, "score": i * 5})

        # Test sort with key function
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pl.sort(key=lambda x: x["score"], reverse=True)
            assert any("memory" in str(warning.message) for warning in w)

        # Verify sort worked
        scores = [item["score"] for item in pl]
        assert scores == sorted(scores, reverse=True)

        # Test reverse
        original_ids = [item["id"] for item in pl]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pl.reverse()
            assert any("memory" in str(warning.message) for warning in w)

        # Verify reverse worked
        new_ids = [item["id"] for item in pl]
        assert new_ids == list(reversed(original_ids))

        # Test list concatenation
        other_items = [{"id": 100, "score": 1000}, {"id": 101, "score": 1010}]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            combined = pl + other_items
            assert any("memory" in str(warning.message) for warning in w)

        assert len(combined) == len(pl) + len(other_items)
        assert combined[-1] == other_items[-1]

        # Test list multiplication
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            multiplied = pl * 2
            assert any("memory" in str(warning.message) for warning in w)

        assert len(multiplied) == len(pl) * 2

    def test_builtin_functions_compatibility(self):
        """Test that PagedList works with Python built-in functions."""
        pl = PagedList(chunk_size=4, disk_path=self.temp_dir)

        # Add test data
        for i in range(10):
            pl.append({"id": i, "value": i * 3, "active": i % 2 == 0})

        # Test len()
        assert len(pl) == 10

        # Test max() and min()
        max_item = max(pl, key=lambda x: x["value"])
        min_item = min(pl, key=lambda x: x["value"])
        assert max_item["value"] == 27  # 9 * 3
        assert min_item["value"] == 0  # 0 * 3

        # Test sorted()
        sorted_items = sorted(pl, key=lambda x: x["id"], reverse=True)
        sorted_ids = [item["id"] for item in sorted_items]
        assert sorted_ids == list(range(9, -1, -1))

        # Test all() and any()
        assert all(item["id"] >= 0 for item in pl)
        assert any(item["active"] for item in pl)
        assert not all(item["active"] for item in pl)

        # Test enumerate()
        enumerated = list(enumerate(pl))
        assert len(enumerated) == 10
        assert enumerated[3][0] == 3  # index
        assert enumerated[3][1]["id"] == 3  # item

        # Test filter()
        active_items = list(filter(lambda x: x["active"], pl))
        assert len(active_items) == 5  # Every other item

        # Test map() (built-in, not the PagedList method)
        doubled_values = list(map(lambda x: x["value"] * 2, pl))
        assert doubled_values[0] == 0
        assert doubled_values[5] == 30  # 5 * 3 * 2

        # Test zip()
        other_list = [f"item_{i}" for i in range(10)]
        zipped = list(zip(pl, other_list))
        assert len(zipped) == 10
        assert zipped[0][1] == "item_0"

        # Test reversed()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reversed_items = list(reversed(pl))

        assert len(reversed_items) == 10
        assert reversed_items[0]["id"] == 9
        assert reversed_items[-1]["id"] == 0

        # Test iter() and next()
        iterator = iter(pl)
        first_item = next(iterator)
        second_item = next(iterator)
        assert first_item["id"] == 0
        assert second_item["id"] == 1

    def test_type_conversions_with_warnings(self):
        """Test converting PagedList to other types."""
        pl = PagedList(chunk_size=3, disk_path=self.temp_dir)

        # Add data that spans multiple chunks
        for i in range(8):
            pl.append({"id": i, "name": f"item_{i}"})

        # Test list() conversion
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            as_list = list(pl)
            # Should warn about memory usage
            assert any("memory" in str(warning.message) for warning in w)

        assert isinstance(as_list, list)
        assert len(as_list) == 8
        assert as_list[0]["id"] == 0

        # Test tuple() conversion
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            as_tuple = tuple(pl)
            # Should warn about memory usage
            assert any("memory" in str(warning.message) for warning in w)

        assert isinstance(as_tuple, tuple)
        assert len(as_tuple) == 8
        assert as_tuple[0]["id"] == 0

    def test_edge_cases_and_error_handling(self):
        """Test edge cases and proper error handling."""
        pl = PagedList(chunk_size=3, disk_path=self.temp_dir)

        # Test empty list operations
        assert len(pl) == 0
        assert list(pl) == []

        with pytest.raises(IndexError):
            _ = pl[0]

        with pytest.raises(IndexError):
            pl.pop()

        # Add some data
        for i in range(5):
            pl.append({"id": i, "data": f"test_{i}"})

        # Test out of bounds access
        with pytest.raises(IndexError):
            _ = pl[10]

        with pytest.raises(IndexError):
            _ = pl[-10]

        # Test invalid operations
        with pytest.raises(ValueError):
            pl.remove({"id": 999, "data": "not_found"})

        with pytest.raises(ValueError):
            pl.index({"id": 999, "data": "not_found"})

        # Test sort without key (should fail for dicts)
        with pytest.raises(TypeError):
            pl.sort()

        # Test invalid types
        with pytest.raises(TypeError):
            pl.append("not a dict")

        with pytest.raises(TypeError):
            pl.extend(["not", "dicts"])

    def test_memory_efficiency_across_chunks(self):
        """Test that chunking actually provides memory efficiency."""
        pl = PagedList(chunk_size=5, disk_path=self.temp_dir, auto_cleanup=False)

        # Add enough data to create multiple chunks
        for i in range(25):
            pl.append({"id": i, "data": f"large_data_string_{i}" * 100})

        # Verify chunking occurred
        assert pl.total_chunks > 0
        assert pl.in_memory_count <= 5  # Should not exceed chunk size

        # Verify chunk files exist
        chunk_files = [f for f in os.listdir(self.temp_dir) if f.startswith("chunk_")]
        assert len(chunk_files) == pl.total_chunks

        # Test that we can still access all data
        assert len(pl) == 25
        assert pl[0]["id"] == 0
        assert pl[24]["id"] == 24
        assert pl[10]["id"] == 10  # Cross-chunk access

        # Test slicing across chunks
        cross_chunk_slice = pl[3:8]
        assert len(cross_chunk_slice) == 5
        assert cross_chunk_slice[0]["id"] == 3
        assert cross_chunk_slice[-1]["id"] == 7

        # Cleanup
        pl.cleanup_chunks()

    def test_context_manager_functionality(self):
        """Test that PagedList works properly as a context manager."""
        temp_dir = tempfile.mkdtemp()

        try:
            chunk_files_before = []

            # Use PagedList in context manager
            with PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False) as pl:
                for i in range(10):
                    pl.append({"id": i, "value": i * 2})

                # Verify data exists and chunks are created
                assert len(pl) == 10
                assert pl.total_chunks > 0

                # Check that chunk files exist
                chunk_files_before = [
                    f for f in os.listdir(temp_dir) if f.startswith("chunk_")
                ]
                assert len(chunk_files_before) > 0

            # After context, chunk files should be cleaned up
            chunk_files_after = [
                f for f in os.listdir(temp_dir) if f.startswith("chunk_")
            ]
            assert len(chunk_files_after) == 0

        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir)

    def test_comprehensive_real_world_scenario(self):
        """Test a comprehensive real-world-like scenario."""
        pl = PagedList(chunk_size=100, disk_path=self.temp_dir)

        # Simulate processing a large dataset
        print("\\nSimulating real-world usage...")

        # 1. Bulk data loading
        print("1. Loading data...")
        users = [
            {
                "id": i,
                "name": f"user_{i:05d}",
                "email": f"user{i}@example.com",
                "score": i * 3.14,
                "active": i % 3 == 0,
                "tags": [f"tag_{j}" for j in range(i % 5)],
            }
            for i in range(1000)
        ]
        pl.extend(users)
        print(f"   Loaded {len(pl)} users across {pl.total_chunks} chunks")

        # 2. Data access and filtering
        print("2. Accessing data...")
        assert pl[0]["id"] == 0
        assert pl[500]["id"] == 500
        assert pl[-1]["id"] == 999

        # 3. Search operations
        print("3. Searching...")
        target_user = {
            "id": 250,
            "name": "user_00250",
            "email": "user250@example.com",
            "score": 250 * 3.14,
            "active": False,
            "tags": [],
        }
        assert target_user in pl

        found_index = pl.index(target_user)
        assert found_index == 250

        # 4. Data modification
        print("4. Modifying data...")
        # Update a user
        pl[100] = {
            "id": 100,
            "name": "updated_user",
            "email": "updated@example.com",
            "score": 999.99,
            "active": True,
            "tags": ["updated"],
        }
        assert pl[100]["name"] == "updated_user"

        # 5. Batch operations with warnings
        print("5. Performing batch operations...")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress warnings for demo

            # Sort by score
            pl.sort(key=lambda x: x["score"])
            assert pl[0]["score"] <= pl[1]["score"]

            # Create a subset
            active_users = [user for user in pl if user["active"]]
            print(f"   Found {len(active_users)} active users")

        # 6. Cleanup
        print("6. Cleaning up...")
        pl.clear()
        assert len(pl) == 0
        assert pl.total_chunks == 0

        print("Real-world scenario completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print statements
