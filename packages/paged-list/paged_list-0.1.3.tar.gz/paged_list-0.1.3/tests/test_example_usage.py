"""
Test to run actual example usage to improve coverage.

This test runs the real example_usage function to ensure
command-line functionality is tested.
"""

import subprocess
import sys


def test_run_example_usage_command():
    """Test running the example usage command via python -m."""
    # Test the demo command
    result = subprocess.run(
        [sys.executable, "-m", "paged_list", "demo"],
        capture_output=True,
        text=True,
        timeout=30,  # Prevent hanging
    )

    assert result.returncode == 0
    assert "PagedList Demo:" in result.stdout
    assert "Demo completed and cleaned up!" in result.stdout


def test_run_basic_module_import():
    """Test basic module functionality."""
    # Test basic import and usage
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import tempfile
from paged_list import PagedList

with tempfile.TemporaryDirectory() as temp_dir:
    pl = PagedList(chunk_size=5, disk_path=temp_dir)
    pl.append({"test": "data"})
    print(f"Length: {len(pl)}")
    print(f"Item: {pl[0]}")
    print("Success!")
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert "Length: 1" in result.stdout
    assert "Success!" in result.stdout


if __name__ == "__main__":
    test_run_example_usage_command()
    test_run_basic_module_import()
    print("All example tests passed!")
