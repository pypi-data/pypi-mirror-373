#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Custom exceptions for the RCK SDK."""

class RCKException(Exception):
    """Base exception for all rck_sdk errors."""
    pass

class RCKConfigurationError(RCKException):
    """Raised when the SDK is not configured correctly."""
    pass

class RCKAPIError(RCKException):
    """Raised when the RCK API returns an error."""
    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        
        # Extract details from the new error format
        self.error_type = None
        self.details = None
        if isinstance(response_body, dict):
            self.error_type = response_body.get("error")
            self.details = response_body.get("details")

    def __str__(self):
        base_message = super().__str__()
        if self.status_code:
            error_str = f"API Error (Status {self.status_code}): {base_message}"
            if self.error_type:
                error_str += f" | Type: {self.error_type}"
            if self.details:
                error_str += f" | Details: {self.details}"
            return error_str
        return f"API Error: {base_message}"
