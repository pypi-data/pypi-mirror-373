import unittest
from velocity.misc.merge import deep_merge


class TestDeepMerge(unittest.TestCase):

    def test_simple_merge(self):
        """Test merging two simple dictionaries with no nested structures."""
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 3, "c": 4}
        result = deep_merge(d1, d2)
        self.assertEqual(result, {"a": 1, "b": 3, "c": 4})

    def test_nested_merge(self):
        """Test merging two dictionaries with nested dictionaries."""
        d1 = {"a": {"x": 1}, "b": 2}
        d2 = {"a": {"y": 2}, "b": 3}
        result = deep_merge(d1, d2)
        self.assertEqual(result, {"a": {"x": 1, "y": 2}, "b": 3})

    def test_list_merge(self):
        """Test merging dictionaries with lists, avoiding duplicates."""
        d1 = {"a": [1, 2], "b": 3}
        d2 = {"a": [2, 3], "b": 4}
        result = deep_merge(d1, d2)
        self.assertEqual(result, {"a": [1, 2, 3], "b": 4})

    def test_deeply_nested_merge(self):
        """Test merging deeply nested dictionaries."""
        d1 = {"a": {"b": {"c": 1}}}
        d2 = {"a": {"b": {"d": 2}}}
        result = deep_merge(d1, d2)
        self.assertEqual(result, {"a": {"b": {"c": 1, "d": 2}}})

    def test_update_true(self):
        """Test updating the first dictionary in place when update=True."""
        d1 = {"a": 1, "b": {"x": 10}}
        d2 = {"b": {"y": 20}, "c": 3}
        result = deep_merge(d1, d2, update=True)
        self.assertEqual(result, {"a": 1, "b": {"x": 10, "y": 20}, "c": 3})
        self.assertEqual(d1, result)  # d1 should be modified in place

    def test_update_false(self):
        """Test creating a new dictionary when update=False (default)."""
        d1 = {"a": 1, "b": {"x": 10}}
        d2 = {"b": {"y": 20}, "c": 3}
        result = deep_merge(d1, d2)
        self.assertEqual(result, {"a": 1, "b": {"x": 10, "y": 20}, "c": 3})
        self.assertNotEqual(d1, result)  # d1 should remain unchanged

    def test_multiple_dicts(self):
        """Test merging multiple dictionaries."""
        d1 = {"a": 1}
        d2 = {"b": 2}
        d3 = {"c": 3}
        result = deep_merge(d1, d2, d3)
        self.assertEqual(result, {"a": 1, "b": 2, "c": 3})

    def test_conflicting_types(self):
        """Test conflicting types (list vs. dict), where latter overrides former."""
        d1 = {"a": {"x": 1}}
        d2 = {"a": [1, 2, 3]}
        result = deep_merge(d1, d2)
        self.assertEqual(result, {"a": [1, 2, 3]})  # d2 overrides d1 here

    def test_empty_dict(self):
        """Test merging with an empty dictionary."""
        d1 = {"a": 1, "b": {"x": 10}}
        d2 = {}
        result = deep_merge(d1, d2)
        self.assertEqual(result, d1)  # merging with empty dict should not change d1

    def test_merge_with_none(self):
        """Test merging where one dictionary has None values."""
        d1 = {"a": 1, "b": None}
        d2 = {"b": 2, "c": None}
        result = deep_merge(d1, d2)
        self.assertEqual(result, {"a": 1, "b": 2, "c": None})


if __name__ == "__main__":
    unittest.main()
