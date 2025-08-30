import unittest
import decimal
from datetime import datetime, date, time, timedelta
from velocity.misc.format import gallons, gallons2liters, currency, human_delta, to_json


class TestYourModule(unittest.TestCase):

    def test_gallons(self):
        """Tests the gallons function with various inputs."""
        self.assertEqual(gallons("10.5"), "10.50")
        self.assertEqual(gallons(10.5), "10.50")
        self.assertEqual(gallons(decimal.Decimal("10.5")), "10.50")
        self.assertEqual(gallons(None), "")
        self.assertEqual(gallons("invalid"), "")

    def test_gallons2liters(self):
        """Tests the gallons2liters function with various inputs."""
        self.assertEqual(gallons2liters("10"), "37.85")  # 10 gallons to liters
        self.assertEqual(gallons2liters(1), "3.79")  # 1 gallon to liters
        self.assertEqual(gallons2liters(decimal.Decimal("1")), "3.79")
        self.assertEqual(gallons2liters(None), "")
        self.assertEqual(gallons2liters("invalid"), "")

    def test_currency(self):
        """Tests the currency function with various inputs."""
        self.assertEqual(currency("1000.5"), "1000.50")
        self.assertEqual(currency(1000.5), "1000.50")
        self.assertEqual(currency(decimal.Decimal("1000.5")), "1000.50")
        self.assertEqual(currency(None), "")
        self.assertEqual(currency("invalid"), "")

    def test_human_delta(self):
        """Tests the human_delta function with various timedelta values."""
        self.assertEqual(human_delta(timedelta(seconds=45)), "45 sec")
        self.assertEqual(human_delta(timedelta(minutes=2, seconds=15)), "2 min 15 sec")
        self.assertEqual(
            human_delta(timedelta(hours=1, minutes=5)), "1 hr(s) 5 min 0 sec"
        )
        self.assertEqual(
            human_delta(timedelta(days=2, hours=4, minutes=30)),
            "2 day(s) 4 hr(s) 30 min 0 sec",
        )

    def test_to_json(self):
        """Tests the to_json function with various custom objects."""
        obj = {
            "name": "Test",
            "price": decimal.Decimal("19.99"),
            "date": date(2023, 1, 1),
            "datetime": datetime(2023, 1, 1, 12, 30, 45),
            "time": time(12, 30, 45),
            "duration": timedelta(days=1, hours=2, minutes=30),
        }
        result = to_json(obj)
        self.assertIn('"price": 19.99', result)
        self.assertIn('"date": "2023-01-01"', result)
        self.assertIn('"datetime": "2023-01-01 12:30:45"', result)
        self.assertIn('"time": "12:30:45"', result)
        self.assertIn('"duration": "1 day(s) 2 hr(s) 30 min 0 sec"', result)


if __name__ == "__main__":
    unittest.main()
