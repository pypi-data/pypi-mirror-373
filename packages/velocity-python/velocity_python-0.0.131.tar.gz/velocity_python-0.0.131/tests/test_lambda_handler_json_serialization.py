"""
Test Lambda Handler JSON Serialization Fix

This test verifies that LambdaHandler.serve() returns a JSON-serializable
dictionary instead of a Response object, preventing the 
"Object of type method is not JSON serializable" error.
"""

import json
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from velocity.aws.handlers.lambda_handler import LambdaHandler
from velocity.aws.handlers.response import Response


class TestLambdaHandlerJSONSerialization(unittest.TestCase):
    """Test cases for Lambda Handler JSON serialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_event = {
            "body": '{"action": "test", "payload": {}}',
            "httpMethod": "POST",
            "headers": {"Content-Type": "application/json"},
            "requestContext": {
                "identity": {
                    "sourceIp": "127.0.0.1",  # localhost test IP for unit testing
                    "userAgent": "test-agent"
                }
            },
            "queryStringParameters": {}
        }
        
        self.test_context = MagicMock()
        self.test_context.function_name = "test-function"

    def test_serve_returns_json_serializable_dict(self):
        """Test that serve() returns a JSON-serializable dictionary."""
        
        # Create handler
        handler = LambdaHandler(self.test_event, self.test_context)
        
        # Mock the transaction decorator to pass through tx
        with patch('velocity.aws.handlers.lambda_handler.engine') as mock_engine:
            def mock_transaction(func):
                def wrapper(*args, **kwargs):
                    mock_tx = MagicMock()
                    return func(mock_tx, *args, **kwargs)
                return wrapper
            
            mock_engine.transaction = mock_transaction
            
            # Call serve method
            result = handler.serve(MagicMock())
            
            # Verify result is a dictionary (JSON-serializable)
            self.assertIsInstance(result, dict)
            
            # Verify it has the expected Lambda response structure
            self.assertIn("statusCode", result)
            self.assertIn("headers", result)
            self.assertIn("body", result)
            
            # Verify the body is a JSON string
            self.assertIsInstance(result["body"], str)
            
            # Verify the entire result can be JSON serialized
            try:
                json.dumps(result)
            except (TypeError, ValueError) as e:
                self.fail(f"Result is not JSON serializable: {e}")

    def test_response_object_has_render_method(self):
        """Test that Response object has a proper render method."""
        response = Response()
        
        # Verify render method exists
        self.assertTrue(hasattr(response, 'render'))
        self.assertTrue(callable(response.render))
        
        # Verify render returns a dictionary
        rendered = response.render()
        self.assertIsInstance(rendered, dict)
        
        # Verify structure
        self.assertIn("statusCode", rendered)
        self.assertIn("headers", rendered)
        self.assertIn("body", rendered)
        
        # Verify JSON serializable
        try:
            json.dumps(rendered)
        except (TypeError, ValueError) as e:
            self.fail(f"Rendered response is not JSON serializable: {e}")

    def test_response_render_vs_raw_object(self):
        """Test the difference between Response object and rendered response."""
        response = Response()
        
        # Raw response object should not be directly JSON serializable
        # (it contains method references)
        with self.assertRaises((TypeError, ValueError)):
            json.dumps(response)
        
        # But rendered response should be JSON serializable
        rendered = response.render()
        try:
            json.dumps(rendered)
        except (TypeError, ValueError) as e:
            self.fail(f"Rendered response should be JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
