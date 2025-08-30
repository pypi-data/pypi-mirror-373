"""
SQS Handler Module

This module provides a base class for handling AWS SQS events in Lambda functions.
It includes logging capabilities, action routing, and error handling.
"""

import json
from typing import Any, Dict

from velocity.aws.handlers import context as VelocityContext
from velocity.aws.handlers.base_handler import BaseHandler


class SqsHandler(BaseHandler):
    """
    Base class for handling SQS events in AWS Lambda functions.

    Provides structured processing of SQS records with automatic action routing,
    logging capabilities, and error handling hooks.
    """

    def __init__(
        self,
        aws_event: Dict[str, Any],
        aws_context: Any,
        context_class=VelocityContext.Context,
    ):
        """
        Initialize the SQS handler.

        Args:
            aws_event: The AWS Lambda event containing SQS records
            aws_context: The AWS Lambda context object
            context_class: The context class to use for processing
        """
        super().__init__(aws_event, aws_context, context_class)

    def serve(self, tx):
        """
        Process all SQS records in the event.

        Args:
            tx: Database transaction object
        """
        records = self.aws_event.get("Records", [])

        for record in records:
            self._process_record(tx, record)

    def _process_record(self, tx, record: Dict[str, Any]):
        """
        Process a single SQS record.

        Args:
            tx: Database transaction object
            record: Individual SQS record to process
        """
        attrs = record.get("attributes", {})
        postdata = {}

        # Parse message body if present
        body = record.get("body")
        if body:
            try:
                postdata = json.loads(body)
            except json.JSONDecodeError as e:
                print(f"Failed to parse SQS message body as JSON: {e}")
                postdata = {"raw_body": body}

        # Create local context for this record
        local_context = self.ContextClass(
            aws_event=self.aws_event,
            aws_context=self.aws_context,
            args=attrs,
            postdata=postdata,
            response=None,
            session=None,
        )

        # Determine action from postdata
        action = postdata.get("action") if isinstance(postdata, dict) else None
        
        # Get the list of actions to execute
        actions = self.get_actions_to_execute(action)

        # Use BaseHandler's execute_actions method
        try:
            self.execute_actions(tx, local_context, actions)
        except Exception as e:
            self.handle_error(tx, local_context, e)

    def OnActionDefault(self, tx, context):
        """
        Default action handler when no specific action is found.

        Args:
            tx: Database transaction object
            context: The context object for this record
        """
        action = context.action() if hasattr(context, "action") else "unknown"
        warning_message = (
            f"[Warn] Action handler not found. Calling default action "
            f"`SqsHandler.OnActionDefault` with the following parameters:\n"
            f"  - action: {action}\n"
            f"  - attrs: {context.args()}\n"
            f"  - postdata: {context.postdata()}"
        )
        print(warning_message)
