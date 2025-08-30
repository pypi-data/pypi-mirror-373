import sys
import traceback
from typing import Any, Dict, List, Optional
from velocity.misc.format import to_json
from support.app import DEBUG


class Response:
    """Class to manage and structure HTTP responses with various actions and custom headers."""

    VALID_VARIANTS = {"success", "error", "warning", "info"}

    def __init__(self):
        """Initialize the Response object with default status, headers, and an empty actions list."""
        self.actions: List[Dict[str, Any]] = []
        self.body: Dict[str, Any] = {"actions": self.actions}
        self.raw: Dict[str, Any] = {
            "statusCode": 200,
            "body": "{}",
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }

    def render(self) -> Dict[str, Any]:
        """
        Finalize the response body as JSON and return the complete response dictionary.

        Returns:
            Dict[str, Any]: The complete HTTP response with headers, status code, and JSON body.
        """
        self.raw["body"] = to_json(self.body)
        return self.raw

    def alert(self, message: str, title: str = "Notification") -> "Response":
        """
        Add an alert action to the response.

        Args:
            message (str): The alert message.
            title (str): Title for the alert. Defaults to "Notification".

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append(
            {
                "action": "alert",
                "payload": {"title": title, "message": message},
            }
        )
        return self

    def toast(self, message: str, variant: str = "success") -> "Response":
        """
        Add a toast notification action to the response with a specified variant.

        Args:
            message (str): The message to display in the toast.
            variant (str): The style variant of the toast (e.g., "success", "error"). Must be one of VALID_VARIANTS.

        Raises:
            ValueError: If the variant is not one of VALID_VARIANTS.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        variant = variant.lower()
        if variant not in self.VALID_VARIANTS:
            raise ValueError(
                f"Notistack variant '{variant}' not in {self.VALID_VARIANTS}"
            )
        self.actions.append(
            {
                "action": "toast",
                "payload": {"options": {"variant": variant}, "message": message},
            }
        )
        return self

    def load_object(self, payload: Dict[str, Any]) -> "Response":
        """
        Add a load-object action to the response with a specified payload.

        Args:
            payload (Dict[str, Any]): The data to load into the response.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append({"action": "load-object", "payload": payload})
        return self

    def update_store(self, payload: Dict[str, Any]) -> "Response":
        """
        Add an update-store action to the response with a specified payload.

        Args:
            payload (Dict[str, Any]): The data to update the store with.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append({"action": "update-store", "payload": payload})
        return self

    def file_download(self, payload: Dict[str, Any]) -> "Response":
        """
        Add a file-download action to the response with a specified payload.

        Args:
            payload (Dict[str, Any]): The data for file download details.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append({"action": "file-download", "payload": payload})
        return self

    def status(self, code: Optional[int] = None) -> int:
        """
        Get or set the status code of the response.

        Args:
            code (Optional[int]): The HTTP status code to set. If None, returns the current status code.

        Returns:
            int: The current status code.
        """
        if code is not None:
            self.raw["statusCode"] = int(code)
        return self.raw["statusCode"]

    def headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get or update the headers of the response.

        Args:
            headers (Optional[Dict[str, str]]): A dictionary of headers to add or update.

        Returns:
            Dict[str, str]: The current headers after updates.
        """
        if headers:
            formatted_headers = {
                self._format_header_key(k): v for k, v in headers.items()
            }
            self.raw["headers"].update(formatted_headers)
        return self.raw["headers"]

    def set_status(self, code: int) -> "Response":
        """
        Set the HTTP status code of the response.

        Args:
            code (int): The status code to set.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.status(code)
        return self

    def set_headers(self, headers: Dict[str, str]) -> "Response":
        """
        Set custom headers for the response.

        Args:
            headers (Dict[str, str]): The headers to add or update.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.headers(headers)
        return self

    def set_body(self, body: Dict[str, Any]) -> "Response":
        """
        Update the body of the response with new data.

        Args:
            body (Dict[str, Any]): The body data to update.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.body.update(body)
        return self

    def exception(self) -> None:
        """
        Capture and format the current exception details and set a 500 status code.
        Includes traceback information if DEBUG mode is enabled.
        """
        exc_type, exc_value, tb = sys.exc_info()
        self.set_status(500)
        self.set_body(
            {
                "python_exception": {
                    "type": str(exc_type),
                    "value": str(exc_value),
                    "traceback": traceback.format_exc() if DEBUG else None,
                    "tb": traceback.format_tb(tb) if DEBUG else None,
                }
            }
        )

    def console(self, message: str, title: str = "Notification") -> "Response":
        """
        Add a console log action to the response.

        Args:
            message (str): The console message.
            title (str): Title for the console message. Defaults to "Notification".

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append(
            {
                "action": "console",
                "payload": {"title": title, "message": message},
            }
        )
        return self

    def redirect(self, location: str) -> "Response":
        """
        Add a redirect action to the response with the target location.

        Args:
            location (str): The URL to redirect to.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append({"action": "redirect", "payload": {"location": location}})
        return self

    def signout(self) -> "Response":
        """
        Add a signout action to the response.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append({"action": "signout"})
        return self

    def set_table(self, payload: Dict[str, Any]) -> "Response":
        """
        Add a set-table action to the response with the specified payload.

        Args:
            payload (Dict[str, Any]): The table data to set.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append({"action": "set-table", "payload": payload})
        return self

    def set_repo(self, payload: Dict[str, Any]) -> "Response":
        """
        Add a set-repo action to the response with the specified payload.

        Args:
            payload (Dict[str, Any]): The repository data to set.

        Returns:
            Response: The current Response object, allowing method chaining.
        """
        self.actions.append({"action": "set-repo", "payload": payload})
        return self

    @staticmethod
    def _format_header_key(key: str) -> str:
        """
        Format HTTP headers to be in a title-cased format.

        Args:
            key (str): The header key to format.

        Returns:
            str: The formatted header key.
        """
        return "-".join(word.capitalize() for word in key.split("-"))
