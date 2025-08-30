"""
Standard Mixin combining ActivityTracker and ErrorHandler.

Provides a single mixin that includes both activity tracking and error handling
with standardized beforeAction, afterAction, and onError implementations.
"""

import copy
import pprint
from abc import ABC, abstractmethod

from .activity_tracker import ActivityTracker
from .error_handler import ErrorHandler


class StandardMixin(ActivityTracker, ErrorHandler):
    """
    Combined mixin providing both activity tracking and error handling.
    Use this as the primary mixin for Lambda handlers.
    
    Provides standard implementations of:
    - beforeAction: Starts activity tracking + custom logic
    - afterAction: Records success + custom logic  
    - onError: Records error + handles notifications + custom logic
    """
    
    def beforeAction(self, tx, context):
        """Standard beforeAction implementation"""
        # Start activity tracking
        self.track_activity_start(tx, context)
        
        # Call any custom beforeAction logic
        self._custom_before_action(tx, context)
    
    def afterAction(self, tx, context):
        """Standard afterAction implementation"""
        # Update activity tracking with success
        self.track_activity_success(tx, context)
        
        # Call any custom afterAction logic
        self._custom_after_action(tx, context)
    
    def onError(self, tx, context, exc, tb):
        """Standard onError implementation"""
        # Convert exc to exception object if it's a string
        if isinstance(exc, str):
            exception = Exception(exc)
        else:
            exception = exc
            
        # Update activity tracking with error
        self.track_activity_error(tx, context, exception, tb)
        
        # Handle error with standard patterns
        self.handle_standard_error(tx, context, exception, tb)
        
        # Call any custom error handling
        self._custom_error_handler(tx, context, exception, tb)
    
    @abstractmethod
    def _custom_before_action(self, tx, context):
        """Override this method for handler-specific beforeAction logic"""
        pass
    
    @abstractmethod  
    def _custom_after_action(self, tx, context):
        """Override this method for handler-specific afterAction logic"""
        pass
    
    @abstractmethod
    def _custom_error_handler(self, tx, context, exception, tb):
        """Override this method for handler-specific error handling"""
        pass
