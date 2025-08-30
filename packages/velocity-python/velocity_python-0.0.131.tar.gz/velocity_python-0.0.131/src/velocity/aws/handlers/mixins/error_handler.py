"""
Error Handler Mixin for Lambda Handlers.

Provides standardized error handling, logging, and notification functionality
for Lambda handlers.
"""

import copy
import os
import pprint
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ErrorHandler(ABC):
    """
    Mixin class providing standardized error handling for Lambda handlers.
    
    Handles error logging to sys_log table, email notifications to administrators,
    and error metrics collection.
    """
    
    def handle_standard_error(self, tx, context, exception: Exception, tb_string: str):
        """Handle errors with consistent logging and notification patterns"""
        
        # Log to sys_log for centralized logging
        self.log_error_to_system(tx, context, exception, tb_string)
        
        # Determine if this error requires notification
        if self._should_notify_error(exception):
            self.send_error_notification(tx, context, exception, tb_string)
        
        # Log error metrics for monitoring
        self.log_error_metrics(tx, context, exception)
    
    def log_error_to_system(self, tx, context, exception: Exception, tb_string: str):
        """Log error to sys_log table"""
        error_data = {
            "level": "ERROR",
            "message": str(exception),
            "function": f"{self.__class__.__name__}.{context.action()}",
            "traceback": tb_string,
            "exception_type": exception.__class__.__name__,
            "handler_name": self.__class__.__name__,
            "action": context.action(),
            "user_branch": os.environ.get("USER_BRANCH", "Unknown"),
            "function_name": os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "Unknown"),
            "app_name": os.environ.get("ProjectName", "Unknown"),
            "user_agent": "AWS Lambda",
            "device_type": "Lambda",
            "sys_modified_by": "Lambda",
        }
        
        # Add user context if available
        try:
            if hasattr(self, 'current_user') and self.current_user:
                error_data["user_email"] = self.current_user.get("email_address")
        except:
            pass
            
        tx.table("sys_log").insert(error_data)
    
    def send_error_notification(self, tx, context, exception: Exception, tb_string: str):
        """Send error notification email to administrators"""
        try:
            # Import here to avoid circular dependency
            from support.app import helpers
            
            environment = os.environ.get('USER_BRANCH', 'Unknown').title()
            function_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'Unknown')
            
            subject = f"{environment} Lambda Error - {function_name}"
            
            body = f"""
Error Details:
- Handler: {self.__class__.__name__}
- Action: {context.action()}
- Exception: {exception.__class__.__name__}
- Message: {str(exception)}
- Environment: {environment}
- Function: {function_name}

Full Traceback:
{tb_string}

Request Details:
{self._get_error_context(context)}
            """
            
            sender = self._get_error_notification_sender()
            recipients = self._get_error_notification_recipients()
            
            helpers.sendmail(
                tx,
                subject=subject,
                body=body,
                html=None,
                sender=sender,
                recipient=recipients[0],
                cc=recipients[1:] if len(recipients) > 1 else None,
                bcc=None,
                email_settings_id=1001,
            )
        except Exception as email_error:
            print(f"Failed to send error notification email: {email_error}")
    
    def _should_notify_error(self, exception: Exception) -> bool:
        """Determine if an error should trigger email notifications"""
        # Don't notify for user authentication errors or validation errors
        non_notification_types = [
            "AuthenticationError", 
            "ValidationError", 
            "ValueError",
            "AlertError"
        ]
        
        exception_name = exception.__class__.__name__
        
        # Check for authentication-related exceptions
        if "Authentication" in exception_name or "Auth" in exception_name:
            return False
            
        return exception_name not in non_notification_types
    
    @abstractmethod
    def _get_error_notification_recipients(self) -> list:
        """
        Get list of email recipients for error notifications.
        
        Must be implemented by the handler class.
        
        Returns:
            List of email addresses to notify when errors occur
            
        Example:
            return ["admin@company.com", "devops@company.com"]
        """
        pass
    
    @abstractmethod
    def _get_error_notification_sender(self) -> str:
        """
        Get email sender for error notifications.
        
        Must be implemented by the handler class.
        
        Returns:
            Email address to use as sender for error notifications
            
        Example:
            return "no-reply@company.com"
        """
        pass
    
    def _get_error_context(self, context) -> str:
        """Get sanitized request context for error reporting"""
        try:
            postdata = context.postdata()
            sanitized = copy.deepcopy(postdata)
            
            # Remove sensitive data
            if "payload" in sanitized and isinstance(sanitized["payload"], dict):
                sanitized["payload"].pop("cognito_user", None)
                
            return pprint.pformat(sanitized)
        except:
            return "Unable to retrieve request context"
    
    def log_error_metrics(self, tx, context, exception: Exception):
        """Log error metrics for monitoring and alerting"""
        try:
            metrics_data = {
                "metric_type": "error_count",
                "handler_name": self.__class__.__name__,
                "action": context.action(),
                "exception_type": exception.__class__.__name__,
                "environment": os.environ.get("USER_BRANCH", "Unknown"),
                "function_name": os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "Unknown"),
                "timestamp": time.time(),
                "sys_modified_by": "Lambda"
            }
            
            # Try to insert into metrics table if it exists
            try:
                tx.table("lambda_metrics").insert(metrics_data)
            except:
                # Metrics table might not exist yet, don't fail error handler
                pass
        except:
            # Don't fail the error handler if metrics logging fails
            pass
