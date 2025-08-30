"""
Legacy Mixin for backward compatibility.

Provides enhanced activity tracking while maintaining existing 
beforeAction/afterAction/onError implementations in handlers.
"""

import os
from .activity_tracker import ActivityTracker
from .error_handler import ErrorHandler


class LegacyMixin(ActivityTracker, ErrorHandler):
    """
    Legacy-compatible mixin that enhances existing handlers without breaking them.
    
    This mixin adds standardized activity tracking and error handling
    while preserving existing beforeAction/afterAction/onError implementations.
    
    Use this when migrating existing handlers that have complex custom logic
    in their action methods.
    """
    
    def _enhanced_before_action(self, tx, context):
        """Enhanced beforeAction that adds activity tracking"""
        # Start activity tracking
        self.track_activity_start(tx, context)
    
    def _enhanced_after_action(self, tx, context):
        """Enhanced afterAction that adds activity tracking"""
        # Update activity tracking with success
        self.track_activity_success(tx, context)
    
    def _enhanced_error_handler(self, tx, context, exc, tb):
        """Enhanced onError that adds standardized error handling"""
        # Convert exc to exception object if it's a string
        if isinstance(exc, str):
            exception = Exception(exc)
        else:
            exception = exc
            
        # Update activity tracking with error
        self.track_activity_error(tx, context, exception, tb)
        
        # Handle error with standard patterns (but don't send duplicate emails)
        self.log_error_to_system(tx, context, exception, tb)
        self.log_error_metrics(tx, context, exception)
        
        # Only send notification if handler doesn't already handle it
        # Check for a flag that handlers can set to indicate they handle their own notifications
        if not getattr(self, '_handles_own_error_notifications', False):
            if self._should_notify_error(exception):
                self.send_error_notification(tx, context, exception, tb)
