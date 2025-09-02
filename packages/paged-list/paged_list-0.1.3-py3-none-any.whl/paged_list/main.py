"""
Command-line interface and demonstration utilities for paged-list.

This module provides entry points for running demonstrations and examples
of the professional disk-backed list implementation.
"""

from .paged_list import PagedList


def demo() -> None:
    """Run a demonstration of the PagedList functionality."""
    print("PagedList Demo:")
    print("================")

    # Create a small demo list
    cl = PagedList(chunk_size=5, disk_path="demo_data")

    # Add some data
    for i in range(10):
        cl.append({"id": i, "name": f"item_{i}", "value": i * 10})

    print(f"Created list with {len(cl)} items")
    print(f"First item: {cl[0]}")
    print(f"Last item: {cl[-1]}")
    print(f"Slice [3:7]: {cl[3:7]}")

    # Cleanup
    cl.cleanup_chunks()
    print("Demo completed and cleaned up!")


def main() -> None:
    """Main entry point for the package."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "example":
        # Import and run the comprehensive example
        try:
            import os
            import sys

            # Add the package root to path to allow importing examples
            package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, package_root)
            from examples.comprehensive_usage import example_usage

            example_usage()
        except ImportError:
            print(
                "Example not available. Please ensure examples/comprehensive_usage.py exists."
            )
    else:
        print(
            "paged-list: A disk-backed list implementation for handling large "
            "datasets efficiently"
        )
        print("\nAvailable commands:")
        print("  demo    - Run a small demonstration")
        print("  example - Run a comprehensive usage example")


if __name__ == "__main__":
    main()
