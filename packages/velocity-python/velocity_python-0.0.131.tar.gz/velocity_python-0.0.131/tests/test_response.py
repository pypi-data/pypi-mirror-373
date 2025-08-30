import unittest
import sys
from unittest.mock import patch, MagicMock

# Mock the support module before importing the module that depends on it
sys.modules["support"] = MagicMock()
sys.modules["support.app"] = MagicMock()
sys.modules["support.app"].DEBUG = True

from velocity.aws.handlers.response import Response  # Replace with actual module path


class TestResponse(unittest.TestCase):

    def setUp(self):
        self.response = Response()

    def test_initial_status_code(self):
        self.assertEqual(self.response.status(), 200)

    def test_set_status_code(self):
        self.response.set_status(404)
        self.assertEqual(self.response.status(), 404)

    def test_initial_headers(self):
        headers = self.response.headers()
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_set_headers(self):
        custom_headers = {"x-custom-header": "value"}
        self.response.set_headers(custom_headers)
        headers = self.response.headers()
        self.assertEqual(headers["X-Custom-Header"], "value")  # Ensures capitalization
        self.assertIn("Content-Type", headers)

    def test_alert_action(self):
        self.response.alert("Test message", "Alert Title")
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "alert")
        self.assertEqual(self.response.actions[0]["payload"]["title"], "Alert Title")
        self.assertEqual(self.response.actions[0]["payload"]["message"], "Test message")

    def test_toast_action_valid_variant(self):
        self.response.toast("Toast message", "warning")
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "toast")
        self.assertEqual(
            self.response.actions[0]["payload"]["options"]["variant"], "warning"
        )

    def test_toast_action_invalid_variant(self):
        with self.assertRaises(ValueError) as context:
            self.response.toast("Invalid toast", "invalid_variant")
        self.assertIn(
            "Notistack variant 'invalid_variant' not in", str(context.exception)
        )

    def test_load_object_action(self):
        payload = {"key": "value"}
        self.response.load_object(payload)
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "load-object")
        self.assertEqual(self.response.actions[0]["payload"], payload)

    def test_update_store_action(self):
        payload = {"key": "value"}
        self.response.update_store(payload)
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "update-store")
        self.assertEqual(self.response.actions[0]["payload"], payload)

    def test_file_download_action(self):
        payload = {"file": "file.txt"}
        self.response.file_download(payload)
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "file-download")
        self.assertEqual(self.response.actions[0]["payload"], payload)

    def test_redirect_action(self):
        self.response.redirect("https://example.com")
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "redirect")
        self.assertEqual(
            self.response.actions[0]["payload"]["location"], "https://example.com"
        )

    def test_signout_action(self):
        self.response.signout()
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "signout")

    def test_set_table_action(self):
        payload = {"table": "data"}
        self.response.set_table(payload)
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "set-table")
        self.assertEqual(self.response.actions[0]["payload"], payload)

    def test_set_repo_action(self):
        payload = {"repo": "data"}
        self.response.set_repo(payload)
        self.assertEqual(len(self.response.actions), 1)
        self.assertEqual(self.response.actions[0]["action"], "set-repo")
        self.assertEqual(self.response.actions[0]["payload"], payload)

    def test_exception_handling_debug_on(self):
        with patch("your_module.DEBUG", True), patch(
            "traceback.format_exc", return_value="formatted traceback"
        ):
            try:
                raise ValueError("Test exception")
            except ValueError:
                self.response.exception()

        self.assertEqual(self.response.status(), 500)
        exception_info = self.response.body["python_exception"]
        self.assertEqual(exception_info["value"], "Test exception")
        self.assertEqual(exception_info["traceback"], "formatted traceback")

    def test_exception_handling_debug_off(self):
        with patch("your_module.DEBUG", False), patch(
            "traceback.format_exc", return_value="formatted traceback"
        ):
            try:
                raise ValueError("Test exception")
            except ValueError:
                self.response.exception()

        self.assertEqual(self.response.status(), 500)
        exception_info = self.response.body["python_exception"]
        self.assertEqual(exception_info["value"], "Test exception")
        self.assertIsNone(exception_info["traceback"])

    def test_chaining_methods(self):
        response = (
            self.response.set_status(201)
            .alert("Chain Alert")
            .toast("Chain Toast", "info")
            .redirect("https://chained-example.com")
        )
        self.assertEqual(response.status(), 201)
        self.assertEqual(len(response.actions), 3)
        self.assertEqual(
            response.actions[2]["payload"]["location"], "https://chained-example.com"
        )

    def test_render(self):
        self.response.set_body({"key": "value"})
        rendered_response = self.response.render()
        self.assertEqual(rendered_response["statusCode"], 200)
        self.assertEqual(
            rendered_response["headers"]["Content-Type"], "application/json"
        )
        self.assertIn('"key": "value"', rendered_response["body"])

    def test_format_header_key(self):
        result = Response._format_header_key("x-custom-header")
        self.assertEqual(result, "X-Custom-Header")


if __name__ == "__main__":
    unittest.main()
