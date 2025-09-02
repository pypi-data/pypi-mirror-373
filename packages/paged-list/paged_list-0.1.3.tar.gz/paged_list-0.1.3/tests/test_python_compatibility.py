"""
Python version compatibility tests for disk-backed list.
"""

import sys
import tempfile

import pytest

from paged_list import PagedList


def test_python_version_support():
    """Test that we're running on a supported Python version."""
    major, minor = sys.version_info[:2]
    assert major == 3, f"Only Python 3 is supported, got Python {major}"
    assert minor >= 9, f"Python 3.9+ required, got Python 3.{minor}"


def test_basic_functionality_all_versions():
    """Test that basic functionality works across Python versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cl = PagedList(disk_path=tmpdir, chunk_size=10)

        # Test basic operations
        cl.append({"id": 1, "value": "test"})
        assert len(cl) == 1
        assert cl[0]["value"] == "test"

        # Test list operations
        cl.extend([{"id": 2, "value": "test2"}, {"id": 3, "value": "test3"}])
        assert len(cl) == 3

        # Test slicing
        subset = cl[1:3]
        assert len(subset) == 2
        assert subset[0]["id"] == 2

        # Test context manager
        with cl as context_cl:
            assert len(context_cl) == 3

        print(f"All basic tests passed on Python {sys.version}")


def test_type_hints_compatibility():
    """Test that type hints work properly across versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # These should not raise type errors
        cl: PagedList = PagedList(disk_path=tmpdir)
        data: dict = {"test": "value"}
        cl.append(data)

        result = cl[0]
        assert isinstance(result, dict)


def test_concurrent_futures_compatibility():
    """Test that concurrent.futures works properly across versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cl = PagedList(disk_path=tmpdir, chunk_size=5)

        # Add enough data to trigger chunking
        for i in range(20):
            cl.append({"id": i, "value": f"item_{i}"})

        # Test map operation (uses ThreadPoolExecutor internally)
        def increment_id(item):
            item["id"] += 1000
            return item

        cl.map(increment_id)

        # Verify the operation worked
        assert cl[0]["id"] >= 1000
        assert cl[10]["id"] >= 1010


@pytest.mark.integration
def test_pathlib_compatibility():
    """Test that pathlib operations work across versions."""
    import pathlib

    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = pathlib.Path(tmpdir) / "custom_data"
        cl = PagedList(disk_path=str(data_path), chunk_size=5)

        cl.append({"test": "pathlib_compatibility"})
        assert len(cl) == 1
        assert data_path.exists()


def test_json_serialization_compatibility():
    """Test JSON serialization across Python versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cl = PagedList(disk_path=tmpdir, chunk_size=5)

        # Add data with various types
        test_data = {
            "string": "test",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        cl.append(test_data)
        cl.serialize()  # Convert complex types to JSON strings

        # Verify serialization worked
        result = cl[0]
        assert isinstance(result["list"], str)  # Should be JSON string now
        assert isinstance(result["dict"], str)  # Should be JSON string now


if __name__ == "__main__":
    test_python_version_support()
    test_basic_functionality_all_versions()
    test_type_hints_compatibility()
    test_concurrent_futures_compatibility()
    test_pathlib_compatibility()
    test_json_serialization_compatibility()
    print("✅ All compatibility tests passed!")
    test_basic_functionality_all_versions()
    test_type_hints_compatibility()
    test_concurrent_futures_compatibility()
    test_pathlib_compatibility()
    test_json_serialization_compatibility()
    print("✅ All compatibility tests passed!")
