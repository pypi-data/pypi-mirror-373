import unittest
import datetime
from velocity.misc.conv.oconv import (
    none,
    phone,
    day_of_week,
    date_conv,
    time_conv,
    timestamp,
    email,
    pointer,
    rot13,
    boolean,
    money,
    round_to,
    ein,
    to_list,
    title,
    lower,
    upper,
    padding,
    pprint,
    string,
)


class TestOconvFunctions(unittest.TestCase):

    def test_none(self):
        self.assertEqual(none("null"), "")
        self.assertEqual(none("None"), "")
        self.assertEqual(none(""), "")
        self.assertEqual(none("valid"), "valid")

    def test_phone(self):
        self.assertEqual(phone("123-456-7890"), "(123) 456-7890")
        self.assertEqual(phone("(123)4567890"), "(123) 456-7890")
        self.assertEqual(phone("invalid"), "")
        self.assertEqual(phone(None), "")

    def test_day_of_week(self):
        self.assertEqual(day_of_week(1), "Monday")
        self.assertEqual(day_of_week("2"), "Tuesday")
        self.assertEqual(day_of_week(5, abbrev=True), "Fri")
        self.assertEqual(day_of_week([1, 2, 5], abbrev=True), "Mon,Tue,Fri")
        self.assertEqual(day_of_week("invalid"), "")

    def test_date_conv(self):
        """Tests the date_conv function with various inputs."""
        self.assertEqual(date_conv(datetime.datetime(2023, 1, 1)), "2023-01-01")
        self.assertEqual(date_conv(datetime.date(2023, 1, 1)), "2023-01-01")
        self.assertEqual(date_conv("not a date"), "not a date")

    def test_time_conv(self):
        """Tests the time_conv function with various inputs."""
        self.assertEqual(
            time_conv(datetime.datetime(2023, 1, 1, 12, 30, 45)), "12:30:45"
        )
        self.assertEqual(time_conv(datetime.time(12, 30, 45)), "12:30:45")
        self.assertEqual(time_conv("invalid"), "invalid")

    def test_timestamp(self):
        self.assertEqual(
            timestamp(datetime.datetime(2023, 1, 1, 12, 30, 45)),
            "Sun Jan  1 12:30:45 2023",
        )
        self.assertEqual(timestamp("invalid"), "invalid")

    def test_email(self):
        self.assertEqual(email("EXAMPLE@domain.com"), "example@domain.com")
        self.assertEqual(email("None"), "")
        self.assertEqual(email(None), "")

    def test_pointer(self):
        self.assertEqual(pointer("123"), 123)
        self.assertEqual(pointer("invalid"), "")
        self.assertEqual(pointer(None), "")

    def test_rot13(self):
        self.assertEqual(rot13("hello"), "uryyb")
        self.assertEqual(rot13("uryyb"), "hello")

    def test_boolean(self):
        self.assertFalse(boolean("false"))
        self.assertTrue(boolean("true"))
        self.assertTrue(boolean(True))
        self.assertFalse(boolean(False))

    def test_money(self):
        self.assertEqual(money("1234.5"), "$1,234.50")
        self.assertEqual(money("-1234.56"), "-$1,234.56")
        self.assertEqual(money("None"), "")
        self.assertEqual(money(None), "")

    def test_round_to(self):
        self.assertEqual(round_to(2, "123.456"), "123.46")
        self.assertEqual(round_to(1, "123.456"), "123.5")
        round_func = round_to(1)
        self.assertEqual(round_func("123.45"), "123.5")

    def test_ein(self):
        self.assertEqual(ein("123456789"), "12-3456789")
        self.assertEqual(ein("12-3456789"), "12-3456789")
        self.assertEqual(ein("invalid"), "")

    def test_to_list(self):
        self.assertEqual(to_list("[1, 2, 3]"), [1, 2, 3])
        self.assertEqual(to_list("single"), ["single"])
        self.assertEqual(to_list(["already", "a", "list"]), ["already", "a", "list"])
        self.assertIsNone(to_list("None"))

    def test_title(self):
        self.assertEqual(title("hello world"), "Hello World")
        self.assertEqual(title("None"), "")
        self.assertEqual(title(None), "")

    def test_lower(self):
        self.assertEqual(lower("HELLO"), "hello")
        self.assertEqual(lower("None"), "")
        self.assertEqual(lower(None), "")

    def test_upper(self):
        self.assertEqual(upper("hello"), "HELLO")
        self.assertEqual(upper("None"), "")
        self.assertEqual(upper(None), "")

    def test_padding(self):
        pad_func = padding(10, " ")
        self.assertEqual(pad_func("123"), "       123")
        self.assertEqual(pad_func(None), "")
        self.assertEqual(padding(5, "0")("12"), "00012")

    def test_pprint(self):
        self.assertEqual(pprint("[1, 2, 3]"), "[1, 2, 3]")
        self.assertEqual(pprint("invalid"), "invalid")

    def test_string(self):
        self.assertEqual(string("text"), "text")
        self.assertEqual(string(None), "")
        self.assertEqual(string(""), "")


if __name__ == "__main__":
    unittest.main()
