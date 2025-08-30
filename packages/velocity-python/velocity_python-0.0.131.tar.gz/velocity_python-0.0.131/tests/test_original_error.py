#!/usr/bin/env python3

# Test script to demonstrate the original error


def test_original_error():
    """Demonstrate the original error that was happening"""

    # Simulate what duplicate_rows() was returning (individual dicts, not groups)
    # The code was expecting groups but getting individual rows
    fake_groups = [
        {
            "sys_id": 1,
            "email_address": "test1@example.com",
            "card_number": "1234",
            "expiration_date": "2024-01",
            "status": None,
        },
        {
            "sys_id": 2,
            "email_address": "test1@example.com",
            "card_number": "1234",
            "expiration_date": "2024-02",
            "status": None,
        },
    ]

    print("Testing original problematic code pattern:")

    for group in fake_groups:  # group is actually a single row/dict
        print(f"Processing 'group': {group}")
        try:
            # This is the line that was failing: sorted(group, key=lambda x: x["expiration_date"])
            # When group is a dict, sorted() iterates over the keys (strings), not the values
            sorted_group = sorted(group, key=lambda x: x["expiration_date"])
            print(f"  Sorted result: {sorted_group}")
        except TypeError as e:
            print(f"  ERROR: {e}")
            print(
                f"  This happened because 'group' is a dict, so sorted() iterates over keys: {list(group.keys())}"
            )
            print(
                f"  The lambda tries to access x['expiration_date'] where x is a string key, not a dict"
            )
            return False

    return True


if __name__ == "__main__":
    print("Demonstrating the original error:")
    test_original_error()
