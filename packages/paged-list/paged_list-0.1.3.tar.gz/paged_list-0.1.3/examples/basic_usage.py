"""
Example usage of disk-backed list package.
"""

from paged_list import PagedList


def basic_example():
    """Run a basic example of PagedList usage."""
    print("Basic PagedList Example")
    print("=========================")

    # Create a PagedList with small chunk size for demonstration
    cl = PagedList(chunk_size=5, disk_path="example_data")

    # Add some data
    print("Adding 12 items...")
    for i in range(12):
        cl.append(
            {
                "id": i,
                "name": f"item_{i}",
                "value": i * 10,
                "metadata": {"category": "test", "active": True},
            }
        )

    print(f"List length: {len(cl)}")
    print(f"Chunks created: {cl.total_chunks}")
    print(f"Items in memory: {cl.in_memory_count}")

    # Demonstrate indexing
    print(f"\nFirst item: {cl[0]}")
    print(f"Last item: {cl[-1]}")
    print(f"Item at index 5: {cl[5]}")

    # Demonstrate slicing
    print(f"\nSlice [3:7]: {cl[3:7]}")

    # Demonstrate updating
    print("\nUpdating item at index 5...")
    cl[5] = {"id": 5, "name": "updated_item_5", "value": 999, "updated": True}
    print(f"Updated item: {cl[5]}")

    # Demonstrate serialization
    print("\nSerializing complex data types...")
    cl.serialize()
    print("Serialization complete - boolean and dict values are now JSON strings")

    # Demonstrate mapping
    print("\nApplying transformation to double all values...")

    def double_value(record):
        if "value" in record and isinstance(record["value"], (int, float)):
            record = record.copy()
            record["value"] *= 2
        return record

    old_value = cl[0]["value"] if "value" in cl[0] else "N/A"
    cl.map(double_value)
    new_value = cl[0]["value"] if "value" in cl[0] else "N/A"
    print(f"First item value changed from {old_value} to {new_value}")

    # Clean up
    print("\nCleaning up...")
    cl.cleanup_chunks()
    print("Example completed!")


def performance_example():
    """Demonstrate performance with larger dataset."""
    print("Performance Example")
    print("===================")

    # Create a larger list
    cl = PagedList(chunk_size=10000, disk_path="perf_data")

    print("Adding 50,000 items...")
    for i in range(50000):
        cl.append(
            {
                "id": i,
                "timestamp": f"2024-01-{(i % 30) + 1:02d}",
                "value": i * 3.14,
                "category": f"category_{i % 10}",
            }
        )

    print(f"Total items: {len(cl)}")
    print(f"Chunks on disk: {cl.total_chunks}")
    print(f"Items in memory: {cl.in_memory_count}")

    # Test random access performance
    import time

    start_time = time.time()

    # Access 1000 random items
    import random

    for _ in range(1000):
        idx = random.randint(0, len(cl) - 1)
        _ = cl[idx]

    end_time = time.time()
    print(f"Time to access 1000 random items: {end_time - start_time:.3f} seconds")

    # Clean up
    cl.cleanup_chunks()
    print("Performance example completed!")


def main():
    """Run the examples."""
    basic_example()
    print("\n" + "=" * 50 + "\n")
    performance_example()


if __name__ == "__main__":
    main()
