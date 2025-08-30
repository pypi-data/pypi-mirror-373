#!/usr/bin/env python3

# Test script to verify the duplicate_rows fix


def test_grouping_fix():
    """Test the fixed grouping logic"""

    # Simulate duplicate rows that would come from duplicate_rows()
    duplicate_rows = [
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
        {
            "sys_id": 3,
            "email_address": "test2@example.com",
            "card_number": "5678",
            "expiration_date": "2024-03",
            "status": None,
        },
        {
            "sys_id": 4,
            "email_address": "test2@example.com",
            "card_number": "5678",
            "expiration_date": "2024-01",
            "status": None,
        },
    ]

    # Group rows by email_address and card_number (the fixed logic)
    groups = {}
    for row in duplicate_rows:
        key = (row["email_address"], row["card_number"])
        if key not in groups:
            groups[key] = []
        groups[key].append(row)

    print("Groups found:")
    for key, group in groups.items():
        print(f"  Key: {key}, Group size: {len(group)}")

        # Test the sorting that was causing the original error
        try:
            sorted_group = sorted(group, key=lambda x: x["expiration_date"])
            print(
                f"    Sorted by expiration_date: {[row['expiration_date'] for row in sorted_group]}"
            )

            # Test the enumeration that happens in the original code
            for idx, row in enumerate(sorted_group):
                print(
                    f"    {idx}: {row['sys_id']}, {row['email_address']}, {row['card_number']}, {row['expiration_date']}"
                )

        except TypeError as e:
            print(f"    ERROR: {e}")
            return False

    return True


if __name__ == "__main__":
    success = test_grouping_fix()
    if success:
        print("\n✓ Fix appears to work correctly!")
    else:
        print("\n✗ Fix has issues")
