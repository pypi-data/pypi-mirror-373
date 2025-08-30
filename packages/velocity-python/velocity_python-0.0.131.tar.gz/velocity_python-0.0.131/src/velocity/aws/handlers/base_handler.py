"""
Base Handler Module

This module provides a base class for handling AWS Lambda events.
It includes common functionality shared between LambdaHandler and SqsHandler.
"""

import os
import sys
import traceback
from typing import Any, Dict, List, Optional

from velocity.aws.handlers import context as VelocityContext


class BaseHandler:
    """
    Base class for handling AWS Lambda events.

    Provides common functionality including action routing, logging,
    and error handling hooks that can be shared across different handler types.
    """

    def __init__(
        self,
        aws_event: Dict[str, Any],
        aws_context: Any,
        context_class=VelocityContext.Context,
    ):
        """
        Initialize the base handler.

        Args:
            aws_event: The AWS Lambda event
            aws_context: The AWS Lambda context object
            context_class: The context class to use for processing
        """
        self.aws_event = aws_event
        self.aws_context = aws_context
        self.serve_action_default = True  # Set to False to disable OnActionDefault
        self.skip_action = False  # Set to True to skip all actions
        self.ContextClass = context_class

        # Configure SSL certificates for HTTPS requests
        self._update_lambda_ca_certificates()

    def _update_lambda_ca_certificates(self):
        """Configure SSL certificates for HTTPS requests in Lambda environments."""
        # This is helpful for running HTTPS clients on lambda.
        if os.path.exists("/opt/python/ca-certificates.crt"):
            os.environ["REQUESTS_CA_BUNDLE"] = "/opt/python/ca-certificates.crt"
        elif os.path.exists("/home/ubuntu/PyLibLayer/ca-certificates.crt"):
            os.environ["REQUESTS_CA_BUNDLE"] = (
                "/home/ubuntu/PyLibLayer/ca-certificates.crt"
            )

    def get_calling_function(self) -> str:
        """
        Get the name of the calling function by inspecting the call stack.

        Returns:
            The name of the calling function or "<Unknown>" if not found
        """
        skip_functions = {"x", "log", "_transaction", "get_calling_function"}

        for idx in range(10):  # Limit search to prevent infinite loops
            try:
                frame = sys._getframe(idx)
                function_name = frame.f_code.co_name

                if function_name not in skip_functions:
                    return function_name

            except ValueError:
                # No more frames in the stack
                break

        return "<Unknown>"

    def format_action_name(self, action: str) -> str:
        """
        Format an action string into a method name.

        Args:
            action: The raw action string (e.g., "create-user", "delete_item")

        Returns:
            Formatted method name (e.g., "OnActionCreateUser", "OnActionDeleteItem")
        """
        if not action:
            return ""

        formatted = action.replace("-", " ").replace("_", " ")
        return f"on action {formatted}".title().replace(" ", "")

    def get_actions_to_execute(self, action: Optional[str]) -> List[str]:
        """
        Get the list of actions to execute.

        Args:
            action: The specific action to execute, if any

        Returns:
            List of action method names to try executing
        """
        actions = []

        # Add specific action if available
        if action:
            action_method = self.format_action_name(action)
            actions.append(action_method)

        # Add default action if enabled
        if self.serve_action_default:
            actions.append("OnActionDefault")

        return actions

    def execute_actions(self, tx, local_context, actions: List[str]) -> bool:
        """
        Execute the appropriate actions for the given context.

        Args:
            tx: Database transaction object
            local_context: The context object
            actions: List of action method names to try

        Returns:
            True if an action was executed, False otherwise
        """
        # Execute beforeAction hook if available
        if hasattr(self, "beforeAction"):
            self.beforeAction(tx, local_context)

        action_executed = False

        # Execute the first matching action
        for action in actions:
            if self.skip_action:
                break

            if hasattr(self, action):
                result = getattr(self, action)(tx, local_context)

                # Check for deprecated return values (LambdaHandler specific)
                if result is not None and hasattr(self, "_check_deprecated_return"):
                    self._check_deprecated_return(action, result)

                action_executed = True
                break

        # Execute afterAction hook if available
        if hasattr(self, "afterAction"):
            self.afterAction(tx, local_context)

        return action_executed

    def handle_error(self, tx, local_context, exception: Exception):
        """
        Handle errors that occur during action execution.

        Args:
            tx: Database transaction object
            local_context: The context object
            exception: The exception that occurred
        """
        if hasattr(self, "onError"):
            self.onError(
                tx,
                local_context,
                exc=exception.__class__.__name__,
                tb=traceback.format_exc(),
            )
        else:
            # Re-raise if no error handler is defined
            raise exception

    def log(self, tx, message: str, function: Optional[str] = None):
        """
        Log a message to the system log table.
        This is a base implementation that should be overridden by subclasses
        to provide handler-specific logging details.

        Args:
            tx: Database transaction object
            message: The message to log
            function: Optional function name, auto-detected if not provided
        """
        if not function:
            function = self.get_calling_function()

        # Base log data - subclasses should extend this
        data = {
            "app_name": os.environ.get("ProjectName", "Unknown"),
            "function": function,
            "message": message,
        }

        # Let subclasses add their specific fields
        self._extend_log_data(data)

        tx.table("sys_log").insert(data)

    def _extend_log_data(self, data: Dict[str, Any]):
        """
        Extend log data with handler-specific fields.
        To be overridden by subclasses.

        Args:
            data: The base log data dictionary to extend
        """
        # Default implementation adds basic Lambda info
        data.update(
            {
                "user_agent": "AWS Lambda",
                "device_type": "Lambda",
                "sys_modified_by": "Lambda",
            }
        )

    def OnActionDefault(self, local_context):
        """
        Default action handler when no specific action is found.

        Args:
            local_context: The context object
        """
        action = getattr(local_context, "action", lambda: "unknown")()
        warning_message = (
            f"[Warn] Action handler not found. Calling default action "
            f"`{self.__class__.__name__}.OnActionDefault` with the following parameters:\n"
            f"  - action: {action}\n"
            f"  - handler: {self.__class__.__name__}"
        )
        print(warning_message)

    def get_context_args(self) -> Dict[str, Any]:
        """
        Get the arguments to pass to the context constructor.
        To be implemented by subclasses based on their specific needs.

        Returns:
            Dictionary of arguments for context initialization
        """
        return {
            "aws_event": self.aws_event,
            "aws_context": self.aws_context,
        }
