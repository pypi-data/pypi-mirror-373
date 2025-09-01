"""
Tests for disk-backed list package.
"""

import tempfile

from paged_list.paged_list import PagedList


def test_paged_list_basic():
    """Test basic PagedList functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=3, disk_path=temp_dir, auto_cleanup=False)

        # Test append
        cl.append({"id": 1, "value": "test"})
        assert len(cl) == 1

        # Test retrieval
        assert cl[0] == {"id": 1, "value": "test"}

        # Test extend
        cl.extend([{"id": 2, "value": "test2"}, {"id": 3, "value": "test3"}])
        assert len(cl) == 3

        # Test chunking (should create a chunk file)
        cl.append({"id": 4, "value": "test4"})
        assert cl.chunk_count == 1
        assert len(cl) == 4

        # Test slicing
        slice_result = cl[1:3]
        assert len(slice_result) == 2
        assert slice_result[0] == {"id": 2, "value": "test2"}

        # Cleanup
        cl.cleanup_chunks()


def test_paged_list_properties():
    """Test PagedList properties."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cl = PagedList(chunk_size=2, disk_path=temp_dir, auto_cleanup=False)

        # Test empty list
        assert cl.is_empty
        assert cl.total_chunks == 0
        assert cl.in_memory_count == 0

        # Add items
        cl.append({"id": 1})
        cl.append({"id": 2})

        assert not cl.is_empty
        # After adding 2 items with chunk_size=2, they get flushed to disk
        assert cl.in_memory_count == 0  # Items are now on disk
        assert cl.total_chunks == 1  # One chunk was created

        # Add one more item
        cl.append({"id": 3})

        assert cl.total_chunks == 1  # Still one chunk
        assert cl.in_memory_count == 1  # One item in memory

        # Cleanup
        cl.cleanup_chunks()


def test_paged_list_context_manager():
    """Test PagedList as context manager."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with PagedList(chunk_size=2, disk_path=temp_dir) as cl:
            cl.append({"id": 1})
            cl.append({"id": 2})
            cl.append({"id": 3})  # This should create a chunk

            assert len(cl) == 3
            assert cl.total_chunks == 1

        # After exiting context, chunks should be cleaned up
        # We can't easily test this without checking the filesystem
