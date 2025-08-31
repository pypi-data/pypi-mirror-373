"""Module containing pytest fixtures for dictionary pattern matching."""

import pytest

from dict_patterns.dict_matcher import DictMatcher


def pytest_configure(config):  # noqa: D103
    pass


@pytest.fixture
def pattern_handlers():
    """
    Fixture that provides an empty dictionary for regex pattern definitions.

    This fixture can be overridden in tests to provide custom regex patterns
    for dictionary matching. Pattern handlers map pattern names to regex strings
    that define what values should match (e.g., {'string': r'[a-zA-Z]+'}).

    Returns:
        dict: Empty dictionary for regex pattern definitions

    """
    return {}


@pytest.fixture
def dict_matcher(pattern_handlers):
    """
    Fixture that provides a DictMatcher instance configured with pattern handlers.

    This fixture creates a DictMatcher with the pattern handlers from the
    pattern_handlers fixture. It can be used to perform dictionary pattern matching
    in tests.

    Args:
        pattern_handlers: Fixture providing custom pattern handlers

    Returns:
        DictMatcher: Configured dictionary matcher instance

    """
    return DictMatcher(pattern_handlers)


@pytest.fixture
def dict_match(dict_matcher):
    """
    Fixture that provides a convenience function for dictionary pattern matching.

    This fixture returns a function that performs pattern matching and returns
    the extracted values. It's a convenience wrapper around the dict_matcher
    fixture that simplifies common testing patterns.

    Args:
        dict_matcher: Fixture providing a DictMatcher instance

    Returns:
        function: A function that takes template and actual dicts and returns
                 the extracted values from successful matches

    """

    def _dict_match(template, actual, partial_match=False):
        dict_matcher.match(template, actual, partial_match=partial_match)
        return dict_matcher.values

    return _dict_match
