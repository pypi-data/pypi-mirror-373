import unittest
from decimal import Decimal
from datetime import date, datetime, time

# Import all functions from iconv.py, renaming any that would clash with built-ins.
from velocity.misc.conv.iconv import (
    none,
    phone,
    day_of_week,
    date_conv,
    time_conv,
    timestamp,
    email,
    integer,
    boolean,
    rot13,
    pointer,
    money,
    round_to,
    decimal_val,
    ein,
    to_list,
    title,
    lower,
    upper,
    padding,
    string,
)


class TestConverters(unittest.TestCase):

    def test_none(self):
        self.assertIsNone(none("None"))
        self.assertIsNone(none("null"))
        self.assertIsNone(none("@null"))
        self.assertIsNone(none(""))
        self.assertIsNone(none("   "))
        self.assertEqual(none("Something"), "Something")

    def test_phone(self):
        self.assertIsNone(phone(None))
        self.assertIsNone(phone("@null"))
        self.assertIsNone(phone("999999"))
        self.assertEqual(phone("1234567890"), "1234567890")
        self.assertEqual(phone("(123) 456-7890"), "1234567890")
        self.assertEqual(phone("1-234-567-8900"), "2345678900")  # leading '1' dropped
        self.assertIsNone(phone("234567890"))  # only 9 digits
        self.assertIsNone(phone("223456789012"))  # 12 digits not valid

    def test_day_of_week(self):
        self.assertEqual(day_of_week("monday"), 1)
        self.assertEqual(day_of_week("Mon"), 1)
        self.assertEqual(day_of_week("TUESDAY"), 2)
        self.assertIsNone(day_of_week("xyz"))
        self.assertIsNone(day_of_week(""))

    def test_date_converter(self):
        self.assertEqual(date_conv("2025-03-07"), date(2025, 3, 7))
        self.assertIsNone(date_conv("2025-99-99"))
        self.assertIsNone(date_conv("None"))
        self.assertIsNone(date_conv("@null"))
        # Test custom format
        self.assertEqual(date_conv("03/07/2025", fmt="%m/%d/%Y"), date(2025, 3, 7))

    def test_time_converter(self):
        self.assertEqual(time_conv("12:34:56"), time(12, 34, 56))
        self.assertIsNone(time_conv("None"))
        self.assertIsNone(time_conv("25:99:99"))
        # Test custom format
        self.assertEqual(time_conv("01-02-03", fmt="%H-%M-%S"), time(1, 2, 3))

    def test_timestamp(self):
        self.assertEqual(
            timestamp("2025-03-07 12:34:56"),
            datetime(2025, 3, 7, 12, 34, 56),
        )
        self.assertIsNone(timestamp("2025-99-99 12:34:56"))
        self.assertIsNone(timestamp("None"))
        # Custom format
        self.assertEqual(
            timestamp("03/07/2025 12|34|56", fmt="%m/%d/%Y %H|%M|%S"),
            datetime(2025, 3, 7, 12, 34, 56),
        )

    def test_email(self):
        self.assertIsNone(email("None"))
        self.assertIsNone(email("not-an-email"))
        self.assertIsNone(email("user@domain"))  # no '.' in domain
        self.assertEqual(email("USER@DOMAIN.COM"), "user@domain.com")

    def test_integer(self):
        self.assertIsNone(integer("None"))
        self.assertIsNone(integer(""))
        self.assertEqual(integer("123"), 123)
        self.assertEqual(integer("+123.45"), 123)
        self.assertEqual(integer("-123.99"), -123)
        self.assertIsNone(integer("123.45.67"))  # multiple decimals

    def test_boolean(self):
        self.assertFalse(boolean("false"))
        self.assertFalse(boolean(""))
        self.assertFalse(boolean("F"))
        self.assertFalse(boolean("0"))
        self.assertFalse(boolean("no"))
        self.assertTrue(boolean("True"))
        self.assertTrue(boolean("any-other-string"))
        self.assertTrue(boolean(True))
        self.assertFalse(boolean(False))
        self.assertFalse(boolean("@null"))

    def test_rot13(self):
        self.assertIsNone(rot13("None"))
        self.assertEqual(rot13("abc"), "nop")
        self.assertEqual(rot13("NOP"), "ABC")

    def test_pointer(self):
        self.assertIsNone(pointer("None"))
        self.assertIsNone(pointer("@null"))
        self.assertIsNone(pointer("@new"))
        self.assertIsNone(pointer("abc"))
        self.assertEqual(pointer("123"), 123)
        self.assertEqual(pointer("-123"), -123)

    def test_money(self):
        self.assertIsNone(money("None"))
        self.assertIsNone(money("abc"))
        self.assertEqual(money("$1,234.56"), Decimal("1234.56"))
        self.assertEqual(money("-$50"), Decimal("-50"))
        self.assertIsNone(money("123.45.67"))

    def test_round_to(self):
        # When passing data directly
        self.assertEqual(round_to(2, "123.456"), Decimal("123.46"))
        self.assertEqual(round_to(0, "123.56"), Decimal("124"))
        self.assertIsNone(round_to(2, "None"))
        self.assertIsNone(round_to(2, "abc"))

        # When using as a converter function
        round_2 = round_to(2)
        self.assertEqual(round_2("123.456"), Decimal("123.46"))
        self.assertIsNone(round_2("abc"))

    def test_decimal_val(self):
        self.assertIsNone(decimal_val("None"))
        self.assertIsNone(decimal_val("abc"))
        self.assertEqual(decimal_val("123.45"), Decimal("123.45"))
        self.assertIsNone(decimal_val("123.45.67"))

    def test_ein(self):
        self.assertIsNone(ein("None"))
        self.assertIsNone(ein("12345678"))  # only 8 digits
        self.assertEqual(ein("12-3456789"), "123456789")
        self.assertEqual(ein("123456789"), "123456789")

    def test_to_list(self):
        self.assertIsNone(to_list("None"))
        self.assertIsNone(to_list("@null"))
        self.assertIsNone(to_list(""))
        # Already list
        self.assertEqual(to_list(["a", "b"]), ["a", "b"])
        # String that looks like a list
        self.assertEqual(to_list("[1, 2, 3]"), [1, 2, 3])
        # Invalid string that starts/ends with []
        self.assertEqual(to_list("[1, x, 3]"), ["[1, x, 3]"])
        # Single element
        self.assertEqual(to_list("banana"), ["banana"])

    def test_title(self):
        self.assertEqual(title("hello world"), "Hello World")
        self.assertEqual(title("HELLO WORLD"), "Hello World")
        self.assertEqual(title(""), "")
        self.assertEqual(title("None"), "")  # because it becomes None -> ""

    def test_lower(self):
        self.assertEqual(lower("Hello"), "hello")
        self.assertEqual(lower(""), "")
        self.assertEqual(lower("NONE"), "")
        self.assertEqual(lower("XYZ"), "xyz")

    def test_upper(self):
        self.assertEqual(upper("Hello"), "HELLO")
        self.assertEqual(upper(""), "")
        self.assertEqual(upper("none"), "")
        self.assertEqual(upper("xyz"), "XYZ")

    def test_padding(self):
        pad_5 = padding(5, "0")
        self.assertIsNone(pad_5("None"))
        self.assertEqual(pad_5("123"), "00123")
        pad_4_star = padding(4, "*")
        self.assertEqual(pad_4_star("AB"), "**AB")
        self.assertIsNone(pad_4_star("None"))

    def test_string(self):
        self.assertIsNone(string("None"))
        self.assertIsNone(string("@null"))
        self.assertIsNone(string(""))
        self.assertEqual(string("hello"), "hello")


if __name__ == "__main__":
    unittest.main()
