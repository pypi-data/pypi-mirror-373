"""
Comprehensive usage example of PagedList demonstrating advanced features.

This example shows a complete workflow including large dataset handling,
serialization, parallel processing, and various list operations.
"""

from typing import Any, Dict

from paged_list import PagedList


def append_data(cl: PagedList, num_items: int) -> None:
    """Appends a specified number of items to the PagedList.

    Args:
        cl (PagedList): The PagedList instance to append data to.
        num_items (int): The number of items to append to the list.
    """
    for i in range(num_items):
        cl.append({"id": i, "value": i * 2})
    print(cl)  # Display object info


def example_usage() -> None:
    """Demonstrate the usage of PagedList."""
    # Create the disk-backed list with chunk size large enough to avoid multiple chunks
    cl = PagedList(chunk_size=5000)  # Large enough to hold all our demo data

    # First appending phase - using smaller numbers for demo (stay under chunk_size)
    num_items = 1500  # Smaller dataset that fits in one chunk
    batch_size = 500
    for i in range(0, num_items, batch_size):
        append_data(cl, batch_size)

    # Verify a single item retrieval
    print(cl[300])

    # Check the length of the list
    print(len(cl))

    # Grab a slice that spans multiple items
    print(cl[299:301])

    # Update an item
    cl[300] = {"id": 300, "value": 42}

    # Show that the item is updated
    print(cl[300])

    # Test extending the list
    cl.extend([{"id": 1501, "value": 43}, {"id": 1502, "value": 44}])

    # show the updated length
    print(f"Length after extending: {len(cl)}")

    # Serialize the list
    # to test serialization lets edit values in the middle of the list
    cl[300] = {
        "id": 300,
        "value": 42,
        "new_value": "hello",
        "new_list": [1, 2, 3],
        "new_dict": {"a": 1, "b": 2},
        "new_bool": True,
    }
    cl.serialize()

    # Test to ensure no instance of list, bool, or dict within the values
    # from cl[250:350] - smaller range
    for record in cl[250:350]:
        for value in record.values():  # type: ignore
            assert not isinstance(
                value, (list, bool, dict)
            ), f"Found instance of {type(value)} in record {record}"
    print("Serialization test passed")

    # Apply a function to all records
    def add_one(record: Dict[str, Any]) -> Dict[str, Any]:
        record["value"] += 1
        return record

    value_before = cl[800]["value"]  # type: ignore
    cl.map(add_one)
    value_after = cl[800]["value"]  # type: ignore
    # Verify the updated value
    assert (
        value_after == value_before + 1
    ), f"Expected {value_before + 1}, got {value_after}"

    print(
        f"The length of the list is {len(cl)} and the length of the list "
        f"converted to a list is {len(list(cl))}"
    )

    cl[10:12] = [
        {"id": 10, "value": 42, "new_value": "hello"},
        {"id": 11, "value": 99, "new_list": [1, 2, 3]},
    ]

    print(cl[10:12])  # Verify update

    # Cleanup disk
    cl.cleanup_chunks()


def main():
    """Run the comprehensive example."""
    print("Comprehensive PagedList Example")
    print("===============================")
    example_usage()
    print("Comprehensive example completed!")


if __name__ == "__main__":
    main()
