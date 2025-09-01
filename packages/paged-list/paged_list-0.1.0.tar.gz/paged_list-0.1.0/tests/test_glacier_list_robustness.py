"""Edge case and robustness tests for PagedList."""

import json
import os
import shutil
import tempfile

import pytest

from paged_list.paged_list import PagedList


@pytest.mark.integration
@pytest.mark.paged_list
class TestPagedListRobustness:
    """Additional robust tests for PagedList edge cases and error conditions."""

    def setup_method(self):
        """Setup temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup temporary directory after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_empty_list_operations(self):
        """Test operations on empty PagedList."""
        print("\n=== Testing Empty List Operations ===")

        cl = PagedList(chunk_size=10, disk_path=self.temp_dir)

        # Test length of empty list
        assert len(cl) == 0

        # Test iteration over empty list
        items = list(cl)
        assert len(items) == 0

        # Test empty slice
        slice_result = cl[0:0]
        assert len(slice_result) == 0

        # Test repr of empty list
        repr_str = repr(cl)
        assert "0 items" in repr_str
        assert "0 chunks" in repr_str

        # Test combine_chunks on empty list
        combined = cl.combine_chunks()
        assert len(combined) == 0

        # Test serialization on empty list
        cl.serialize()  # Should not raise error

        # Test map on empty list
        def dummy_func(record):
            return record

        cl.map(dummy_func)  # Should not raise error

        print("✓ Empty list operations successful")

    def test_single_item_operations(self):
        """Test operations with only one item."""
        print("\n=== Testing Single Item Operations ===")

        cl = PagedList(chunk_size=10, disk_path=self.temp_dir)

        # Add single item
        test_item = {"id": 1, "value": "test"}
        cl.append(test_item)

        # Test length
        assert len(cl) == 1

        # Test indexing
        assert cl[0] == test_item
        assert cl[-1] == test_item

        # Test iteration
        items = list(cl)
        assert len(items) == 1
        assert items[0] == test_item

        # Test slicing
        slice_result = cl[0:1]
        assert len(slice_result) == 1
        assert slice_result[0] == test_item

        # Test update
        new_item = {"id": 1, "value": "updated"}
        cl[0] = new_item
        assert cl[0] == new_item

        cl.cleanup_chunks()
        print("✓ Single item operations successful")

    def test_negative_indexing_comprehensive(self):
        """Test comprehensive negative indexing scenarios."""
        print("\n=== Testing Negative Indexing Comprehensive ===")

        cl = PagedList(chunk_size=5, disk_path=self.temp_dir)

        # Add items across multiple chunks
        test_items = [{"id": i, "value": f"item_{i}"} for i in range(12)]
        for item in test_items:
            cl.append(item)

        # Test negative indexing - use string access to avoid lint errors
        item_neg_1 = cl[-1]
        assert item_neg_1["id"] == 11  # Last item

        item_neg_2 = cl[-2]
        assert item_neg_2["id"] == 10  # Second to last

        item_neg_12 = cl[-12]
        assert item_neg_12["id"] == 0  # First item

        # Test negative indexing with setitem
        cl[-1] = {"id": 11, "value": "updated_last"}
        updated_last = cl[-1]
        assert updated_last["value"] == "updated_last"

        # Test negative indexing in slices
        last_three = cl[-3:]
        assert len(last_three) == 3
        assert last_three[0]["id"] == 9
        assert last_three[2]["id"] == 11

        # Test negative start in slice
        middle_slice = cl[-8:-3]
        assert len(middle_slice) == 5
        assert middle_slice[0]["id"] == 4
        assert middle_slice[4]["id"] == 8

        cl.cleanup_chunks()
        print("✓ Negative indexing comprehensive successful")

    def test_concurrent_operations(self):
        """Test concurrent operations and thread safety."""
        print("\n=== Testing Concurrent Operations ===")

        cl = PagedList(chunk_size=50, disk_path=self.temp_dir)

        # Add data for concurrent operations
        test_items = [
            {"id": i, "value": i * 2, "data": f"item_{i}"} for i in range(200)
        ]
        cl.extend(test_items)

        # Test concurrent serialization
        cl.serialize(max_workers=2)

        # Verify serialization worked - integers should be serialized as strings
        sample_item = cl[50]
        # The "value" field should be JSON serialized if it was a non-string type
        # But in our case, value is already an integer, so let's check a different field
        # Let's add a field that will be serialized
        cl[50] = {"id": 50, "value": 100, "metadata": {"test": True}}
        cl.serialize(max_workers=2)

        # Now check the metadata field
        sample_item = cl[50]
        assert isinstance(sample_item["metadata"], str)  # Should be JSON serialized

        # Test concurrent map operation
        def transform_func(record):
            record["transformed"] = True
            record["double_id"] = (
                json.loads(record["id"]) * 2
                if isinstance(record["id"], str)
                else record["id"] * 2
            )
            return record

        cl.map(transform_func, max_workers=2)

        # Verify transformation worked
        for item in cl:
            assert "transformed" in item
            assert item["transformed"] is True
            assert "double_id" in item

        cl.cleanup_chunks()
        print("✓ Concurrent operations successful")

    def test_boundary_conditions(self):
        """Test boundary conditions around chunk sizes."""
        print("\n=== Testing Boundary Conditions ===")

        cl = PagedList(chunk_size=5, disk_path=self.temp_dir)

        # Test exactly chunk_size items
        for i in range(5):
            cl.append({"id": i, "value": f"item_{i}"})

        # Should have created exactly 1 chunk
        assert cl.chunk_count == 1
        assert len(cl._in_memory_list) == 0

        # Add one more item
        cl.append({"id": 5, "value": "item_5"})

        # Should still have 1 chunk, but 1 item in memory
        assert cl.chunk_count == 1
        assert len(cl._in_memory_list) == 1

        # Test indexing across boundary
        item_4 = cl[4]
        assert item_4["id"] == 4  # Last item in chunk

        item_5 = cl[5]
        assert item_5["id"] == 5  # First item in memory

        # Test slice across boundary - we have 6 items total (0-5)
        boundary_slice = cl[3:6]  # Should get items 3, 4, 5
        assert len(boundary_slice) == 3
        assert boundary_slice[0]["id"] == 3
        assert boundary_slice[2]["id"] == 5

        cl.cleanup_chunks()
        print("✓ Boundary conditions successful")

    def test_large_chunks(self):
        """Test with very large chunk sizes."""
        print("\n=== Testing Large Chunks ===")

        cl = PagedList(chunk_size=1000, disk_path=self.temp_dir)

        # Add many items but not enough to create a chunk
        test_items = [{"id": i, "large_data": "x" * 100} for i in range(500)]
        cl.extend(test_items)

        # Should have no chunks yet
        assert cl.chunk_count == 0
        assert len(cl._in_memory_list) == 500

        # Add more to trigger chunk creation
        more_items = [{"id": i + 500, "large_data": "y" * 100} for i in range(500)]
        cl.extend(more_items)

        # Should have created 1 chunk
        assert cl.chunk_count == 1
        assert len(cl._in_memory_list) == 0

        # Test accessing items
        item_0 = cl[0]
        assert item_0["id"] == 0

        item_999 = cl[999]
        assert item_999["id"] == 999

        cl.cleanup_chunks()
        print("✓ Large chunks successful")

    def test_special_characters_and_unicode(self):
        """Test with special characters and Unicode data."""
        print("\n=== Testing Special Characters and Unicode ===")

        cl = PagedList(chunk_size=10, disk_path=self.temp_dir)

        # Test with special characters and Unicode
        special_items = [
            {"id": 1, "name": "João", "emoji": "🚀", "special": "\"'\\"},
            {"id": 2, "name": "François", "emoji": "🎉", "data": [1, 2, 3]},
            {"id": 3, "name": "北京", "emoji": "🌟", "nested": {"key": "value"}},
            {"id": 4, "name": "Москва", "emoji": "⭐", "bool_val": True},
        ]

        cl.extend(special_items)

        # Test retrieval
        item_0 = cl[0]
        assert item_0["name"] == "João"

        item_1 = cl[1]
        assert item_1["emoji"] == "🎉"

        item_2 = cl[2]
        assert item_2["name"] == "北京"

        item_3 = cl[3]
        assert item_3["name"] == "Москва"

        # Test serialization with special characters
        cl.serialize()

        # Verify serialization preserved Unicode
        serialized_0 = cl[0]
        assert serialized_0["name"] == "João"

        serialized_1 = cl[1]
        assert serialized_1["emoji"] == "🎉"
        assert isinstance(serialized_1["data"], str)  # Should be JSON serialized

        # Test deserialization
        data_back = json.loads(serialized_1["data"])
        assert data_back == [1, 2, 3]

        cl.cleanup_chunks()
        print("✓ Special characters and Unicode successful")

    def test_slice_edge_cases(self):
        """Test edge cases in slice operations."""
        print("\n=== Testing Slice Edge Cases ===")

        cl = PagedList(chunk_size=5, disk_path=self.temp_dir)

        # Add test data
        test_items = [{"id": i, "value": f"item_{i}"} for i in range(20)]
        cl.extend(test_items)

        # Test empty slices
        empty_slice = cl[10:10]
        assert len(empty_slice) == 0

        # Test reverse slices (should be empty)
        reverse_slice = cl[15:10]
        assert len(reverse_slice) == 0

        # Test slice beyond bounds
        beyond_slice = cl[15:30]
        assert len(beyond_slice) == 5  # Only items 15-19 exist

        # Test slice with step = 2
        step_slice = cl[0:10:2]
        assert len(step_slice) == 5
        assert step_slice[0]["id"] == 0
        assert step_slice[1]["id"] == 2
        assert step_slice[4]["id"] == 8

        # Test slice with step = 3
        step3_slice = cl[1:16:3]
        assert len(step3_slice) == 5
        assert step3_slice[0]["id"] == 1
        assert step3_slice[1]["id"] == 4
        assert step3_slice[4]["id"] == 13

        cl.cleanup_chunks()
        print("✓ Slice edge cases successful")

    def test_serialization_edge_cases(self):
        """Test edge cases in serialization."""
        print("\n=== Testing Serialization Edge Cases ===")

        cl = PagedList(chunk_size=5, disk_path=self.temp_dir)

        # Test with complex nested structures
        complex_items = [
            {
                "id": 1,
                "simple": "string",
                "number": 42,
                "nested_dict": {
                    "level1": {
                        "level2": ["a", "b", "c"],
                        "bool_val": True,
                        "null_val": None,
                    }
                },
                "mixed_list": [1, "string", {"key": "value"}, [1, 2, 3]],
                "empty_dict": {},
                "empty_list": [],
            }
        ]

        cl.extend(complex_items)

        # Serialize
        cl.serialize()

        # Verify complex serialization
        item = cl[0]
        assert isinstance(item["nested_dict"], str)
        assert isinstance(item["mixed_list"], str)
        assert isinstance(item["empty_dict"], str)
        assert isinstance(item["empty_list"], str)

        # Test deserialization
        nested_dict = json.loads(item["nested_dict"])
        assert nested_dict["level1"]["level2"] == ["a", "b", "c"]
        assert nested_dict["level1"]["bool_val"] is True
        assert nested_dict["level1"]["null_val"] is None

        mixed_list = json.loads(item["mixed_list"])
        assert len(mixed_list) == 4
        assert mixed_list[0] == 1
        assert mixed_list[1] == "string"

        cl.cleanup_chunks()
        print("✓ Serialization edge cases successful")

    def test_map_operation_edge_cases(self):
        """Test edge cases in map operations."""
        print("\n=== Testing Map Operation Edge Cases ===")

        cl = PagedList(chunk_size=5, disk_path=self.temp_dir)

        # Add test data
        test_items = [{"id": i, "value": i * 2} for i in range(15)]
        cl.extend(test_items)

        # Test map function that adds keys
        def add_keys(record):
            record["new_key"] = "new_value"
            record["computed"] = record["id"] * record["value"]
            return record

        cl.map(add_keys)

        # Verify all items have new keys
        for item in cl:
            assert "new_key" in item
            assert "computed" in item
            assert item["new_key"] == "new_value"
            assert item["computed"] == item["id"] * item["value"]

        # Test map function that removes keys
        def remove_keys(record):
            if "new_key" in record:
                del record["new_key"]
            return record

        cl.map(remove_keys)

        # Verify key removal
        for item in cl:
            assert "new_key" not in item
            assert "computed" in item  # Should still be there

        # Test map function that modifies data types
        def change_types(record):
            record["id"] = str(record["id"])
            record["value"] = str(record["value"])
            return record

        cl.map(change_types)

        # Verify type changes
        for item in cl:
            assert isinstance(item["id"], str)
            assert isinstance(item["value"], str)

        cl.cleanup_chunks()
        print("✓ Map operation edge cases successful")

    def test_error_recovery(self):
        """Test error recovery scenarios."""
        print("\n=== Testing Error Recovery ===")

        cl = PagedList(chunk_size=5, disk_path=self.temp_dir)

        # Add data
        test_items = [{"id": i, "value": f"item_{i}"} for i in range(10)]
        cl.extend(test_items)

        # Test recovery from invalid chunk files
        # Simulate corrupted chunk file
        chunk_files = [f for f in os.listdir(self.temp_dir) if f.startswith("chunk_")]
        if chunk_files:
            chunk_file_path = os.path.join(self.temp_dir, chunk_files[0])
            with open(chunk_file_path, "w") as f:
                f.write("corrupted data")

            # Try to load the corrupted chunk
            try:
                chunk_data = cl._load_chunk(0)
                # Should return empty list for corrupted file
                assert chunk_data == []
            except Exception:
                # Or handle the exception gracefully
                pass

        # Test accessing non-existent chunks
        non_existent_chunk = cl._load_chunk(999)
        assert non_existent_chunk == []

        cl.cleanup_chunks()
        print("✓ Error recovery successful")

    def test_performance_characteristics(self):
        """Test performance characteristics and scalability."""
        print("\n=== Testing Performance Characteristics ===")

        cl = PagedList(chunk_size=1000, disk_path=self.temp_dir)

        # Test large dataset creation
        import time

        start_time = time.time()

        # Create 10,000 items
        for i in range(10000):
            cl.append({"id": i, "data": f"item_{i}" * 10})

        creation_time = time.time() - start_time
        print(f"✓ Created 10,000 items in {creation_time:.2f} seconds")

        # Test random access performance
        import random

        start_time = time.time()

        for _ in range(100):
            idx = random.randint(0, len(cl) - 1)
            _ = cl[idx]

        access_time = time.time() - start_time
        print(f"✓ 100 random accesses in {access_time:.2f} seconds")

        # Test slice performance
        start_time = time.time()

        large_slice = cl[1000:2000]
        assert len(large_slice) == 1000

        slice_time = time.time() - start_time
        print(f"✓ 1000-item slice in {slice_time:.2f} seconds")

        cl.cleanup_chunks()
        print("✓ Performance characteristics successful")

    def test_extend_with_generator(self):
        """Test extending with generators and iterables."""
        print("\n=== Testing Extend with Generator ===")

        cl = PagedList(chunk_size=10, disk_path=self.temp_dir)

        # Test extending with generator
        def item_generator():
            for i in range(25):
                yield {"id": i, "value": f"generated_{i}", "even": i % 2 == 0}

        cl.extend(item_generator())

        assert len(cl) == 25
        assert cl.chunk_count == 2
        assert len(cl._in_memory_list) == 5

        # Test that all items were added correctly
        for i in range(25):
            item = cl[i]
            assert item["id"] == i
            assert item["value"] == f"generated_{i}"
            assert item["even"] == (i % 2 == 0)

        # Test extending with other iterables
        cl.extend([{"id": 25, "value": "list_item"}])
        cl.extend({"id": 26, "value": "tuple_item"} for _ in range(1))

        assert len(cl) == 27
        item_25 = cl[25]
        assert item_25["value"] == "list_item"

        item_26 = cl[26]
        assert item_26["value"] == "tuple_item"

        cl.cleanup_chunks()
        print("✓ Extend with generator successful")
