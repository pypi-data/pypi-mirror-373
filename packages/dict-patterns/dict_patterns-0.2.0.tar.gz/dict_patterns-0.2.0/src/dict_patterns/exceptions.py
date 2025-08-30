"""
Custom exceptions for the dictionary patterns library.

This module provides a hierarchy of exceptions that are specific to dictionary pattern
matching operations, making it easier for users to handle different types of
errors that can occur during pattern matching.
"""


class DictPatternError(Exception):
    """Base exception for all dictionary pattern matching errors."""

    def __init__(self, message: str, path: str = None):
        """Initialize the exception with a message and optional path."""
        self.message = message
        self.path = path
        super().__init__(self.message)


class DictStructureError(DictPatternError):
    """Raised when there are structural mismatches between template and actual dictionary."""

    def __init__(self, message: str, path: str = None):
        """Initialize the exception with a message and optional path."""
        super().__init__(message, path)


class DictKeyMismatchError(DictStructureError):
    """Raised when dictionary keys don't match between template and actual."""

    def __init__(self, path: str):
        """Initialize the exception with the path where keys don't match."""
        message = f"Keys at {path} do not match"
        super().__init__(message, path)


class DictListLengthMismatchError(DictStructureError):
    """Raised when lists have different lengths."""

    def __init__(self, path: str):
        """Initialize the exception with the path where lists have different lengths."""
        message = f"Lists at {path} do not match, they have different lengths"
        super().__init__(message, path)


class DictValueMismatchError(DictPatternError):
    """Raised when values don't match between template and actual."""

    def __init__(self, path: str, template_value=None, actual_value=None):
        """Initialize the exception with path and optional template/actual values."""
        message = f"Values at {path} do not match"
        if template_value is not None and actual_value is not None:
            message += f" (template: {template_value}, actual: {actual_value})"
        super().__init__(message, path)
        self.template_value = template_value
        self.actual_value = actual_value


class DictPatternMatchError(DictPatternError):
    """Raised when pattern matching fails."""

    def __init__(self, path: str, template: str, actual: str):
        """Initialize the exception with path, template, and actual string values."""
        message = f"Strings at {path} = {actual} do not match the pattern {template}"
        super().__init__(message, path)
        self.template = template
        self.actual = actual


class DictPatternValueInconsistencyError(DictPatternError):
    """Raised when the same pattern identifier has different values across matches."""

    def __init__(self, path: str, identifier: str, expected_value: str, actual_value: str):
        """Initialize the exception with path, identifier, and expected/actual values."""
        message = f"Values at {path}.{identifier} do not match (expected: {expected_value}, actual: {actual_value})"
        super().__init__(message, path)
        self.identifier = identifier
        self.expected_value = expected_value
        self.actual_value = actual_value


class DictPatternTypeError(DictPatternError):
    """Raised when an unknown pattern type is encountered."""

    def __init__(self, pattern_name: str, available_patterns: list = None):
        """Initialize the exception with pattern name and optional available patterns."""
        message = f"Unknown pattern type: {pattern_name}"
        if available_patterns:
            message += f" (available: {', '.join(available_patterns)})"
        super().__init__(message)
        self.pattern_name = pattern_name
        self.available_patterns = available_patterns
