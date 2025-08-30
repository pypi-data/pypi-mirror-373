import unittest
from unittest.mock import MagicMock, patch
import numbers
from functools import wraps
from velocity.db import exceptions
from velocity.misc.db import NOTNULL, join, randomword, return_default, NotSupported


class TestNotSupported(unittest.TestCase):
    def test_not_supported(self):
        with self.assertRaises(Exception) as context:
            NotSupported()
        self.assertEqual(
            str(context.exception),
            "Sorry, the driver for this database is not installed",
        )


class TestNOTNULL(unittest.TestCase):
    def test_notnull(self):
        self.assertTrue(NOTNULL(("key", "value")))
        self.assertFalse(NOTNULL(("key", None)))
        self.assertFalse(NOTNULL(("key",)))
        self.assertFalse(NOTNULL(()))


class TestJoin(unittest.TestCase):
    def test_or(self):
        self.assertEqual(join._or("a=1", "b=2"), "(a=1 or b=2)")

    def test_and(self):
        self.assertEqual(join._and("a=1", "b=2"), "(a=1 and b=2)")

    def test_list(self):
        result = join._list("a=1", key1=123, key2="value")
        self.assertIn("a=1", result)
        self.assertIn("key1=123", result)
        self.assertIn("key2='value'", result)


class TestRandomWord(unittest.TestCase):
    def test_randomword_length_specified(self):
        word = randomword(10)
        self.assertEqual(len(word), 10)
        self.assertTrue(word.islower())

    def test_randomword_length_random(self):
        word = randomword()
        self.assertTrue(5 <= len(word) <= 15)
        self.assertTrue(word.islower())


class TestReturnDefault(unittest.TestCase):
    def setUp(self):
        class MockTransaction:
            def create_savepoint(self, cursor):
                return "savepoint"

            def rollback_savepoint(self, sp, cursor):
                pass

            def release_savepoint(self, sp, cursor):
                pass

        class MockTable:
            cursor = MagicMock()

        class MockClass:
            tx = MockTransaction()
            table = MockTable()

            @return_default(default="default_value")
            def func(self, raise_exception=False):
                if raise_exception:
                    raise exceptions.DbApplicationError("Test error")
                return "result"

        self.mock_obj = MockClass()

    def test_return_default_no_exception(self):
        result = self.mock_obj.func(raise_exception=False)
        self.assertEqual(result, "result")

    def test_return_default_with_exception(self):
        result = self.mock_obj.func(raise_exception=True)
        self.assertEqual(result, "default_value")


if __name__ == "__main__":
    unittest.main()
