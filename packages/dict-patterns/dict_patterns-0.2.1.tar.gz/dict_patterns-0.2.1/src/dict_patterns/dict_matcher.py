"""
A class for matching dictionary objects using pattern-based templates.

The DictMatcher allows you to compare two dictionary objects where one can contain
pattern placeholders (e.g., {string:name}) that will be matched against
corresponding values in the other object. Matched values are stored and can
be reused for consistency across multiple matches.
"""

from dict_patterns.exceptions import (
    DictKeyMismatchError,
    DictListLengthMismatchError,
    DictPatternMatchError,
    DictPatternValueInconsistencyError,
    DictValueMismatchError,
)
from dict_patterns.patterns import compile_template


class DictMatcher:
    r"""
    A class for matching dictionary objects using pattern-based templates.

    The DictMatcher allows you to compare two dictionary objects where one can contain
    pattern placeholders (e.g., {string:name}) that will be matched against
    corresponding values in the other object. Matched values are stored and can
    be reused for consistency across multiple matches.

    Parameters
    ----------
    pattern_handlers : dict
        A dictionary mapping pattern names to their corresponding regex patterns.
        For example: {'string': r'[a-zA-Z]+', 'number': r'\\d+'}

    Attributes
    ----------
    pattern_handlers : dict
        The pattern handlers dictionary passed during initialization.
    values : dict
        A dictionary storing matched values for each pattern type, organized by
        pattern name and identifier.

    Examples
    --------
    >>> pattern_handlers = {
    ...     'string': r'[a-zA-Z]+',
    ...     'number': r'\\d+'
    ... }
    >>> matcher = DictMatcher(pattern_handlers)
    >>>
    >>> left = {'name': '{string:user_name}', 'age': '{number:user_age}'}
    >>> right = {'name': 'John', 'age': '25'}
    >>> matcher.match(left, right)
    >>> print(matcher.values)
    {'string': {'user_name': 'John'}, 'number': {'user_age': '25'}}

    """

    def __init__(self, pattern_handlers: dict):
        """
        Initialize the DictMatcher with pattern handlers.

        Parameters
        ----------
        pattern_handlers : dict
            Dictionary mapping pattern names to regex patterns.

        """
        self.pattern_handlers = pattern_handlers
        self.values = {}
        self.__reset_values()

    def __reset_values(self):
        """
        Reset the values dictionary to empty state for each pattern type.

        This method is called internally to clear previous match results
        before performing a new match operation.
        """
        self.values = {key: {} for key in self.pattern_handlers}

    def match(self, template: dict, actual: dict, partial_match: bool = False) -> None:
        """
        Match two dictionary objects using pattern templates.

        This method compares the template object (which may contain pattern placeholders)
        against the actual object (which contains actual values). Pattern matches
        are stored in the `values` attribute for later use.

        Parameters
        ----------
        template : dict
            The template object that may contain pattern placeholders.
            Keys must match exactly with the right object.
        actual : dict
            The actual object to match against. This object should contain
            concrete values that match the patterns in the left object.
        partial_match : bool
            Whether to allow partial matching of the template.

        Raises
        ------
        ValueError
            If the objects don't match according to the pattern rules, or if
            lists have different lengths, or if pattern values are inconsistent
            across multiple matches.

        Examples
        --------
        >>> matcher = DictMatcher({'string': r'[a-zA-Z]+'})
        >>> template = {'user': '{string:name}'}
        >>> actual = {'user': 'Alice'}
        >>> matcher.match(template, actual)  # No exception raised
        >>> matcher.values['string']['name']
        'Alice'

        """
        self.__reset_values()
        self._match(template, actual, "$", partial_match)

    def _match(self, template: dict, actual: dict, path: str, partial_match: bool = False) -> None:
        """
        Recursively match nested dictionary objects.

        This is an internal method that handles the recursive matching of
        nested dictionaries, lists, and pattern-based string matching.

        Parameters
        ----------
        template : dict
            The template object (left side of comparison).
        actual : dict
            The actual object (right side of comparison).
        path : str
            The current path in the dictionary structure for error reporting.
            Uses dot notation (e.g., "$.user.profile.name").
        partial_match : bool
            Whether to allow partial matching of the template.

        Raises
        ------
        ValueError
            If objects don't match at any level, with detailed path information.

        """
        if template.keys() != actual.keys() and not partial_match:
            raise DictKeyMismatchError(path)

        for key, template_value in template.items():
            if key not in actual:
                raise DictKeyMismatchError(f"{path}.{key}")

            actual_value = actual[key]
            current_path = f"{path}.{key}"

            self._match_value(template_value, actual_value, current_path, partial_match)

    def _match_value(self, template_value, actual_value, path: str, partial_match: bool = False) -> None:
        """
        Match a single value pair based on their types.

        Parameters
        ----------
        template_value
            The template value to match against.
        actual_value
            The actual value to match.
        path : str
            The current path for error reporting.
        partial_match : bool
            Whether to allow partial matching of the template.

        """
        if isinstance(template_value, dict) and isinstance(actual_value, dict):
            self._match_dict(template_value, actual_value, path, partial_match)
        elif isinstance(template_value, list) and isinstance(actual_value, list):
            self._match_list(template_value, actual_value, path, partial_match)
        elif isinstance(template_value, str) and isinstance(actual_value, str):
            self._match_string(template_value, actual_value, path)
        elif template_value != actual_value:
            raise DictValueMismatchError(path, template_value, actual_value)

    def _match_dict(self, template: dict, actual: dict, path: str, partial_match: bool = False) -> None:
        """Match two dictionary values recursively."""
        self._match(template, actual, path, partial_match)

    def _match_list(self, template: list, actual: list, path: str, partial_match: bool = False) -> None:
        """Match two list values element by element."""
        if len(template) != len(actual):
            raise DictListLengthMismatchError(path)

        for i, (template_item, actual_item) in enumerate(zip(template, actual, strict=True)):
            self._match_value(template_item, actual_item, f"{path}[{i}]", partial_match)

    def _match_string(self, template: str, actual: str, path: str) -> None:
        """Match two string values, handling pattern placeholders."""
        if not self.pattern_handlers:
            # No pattern handlers, do direct comparison
            if template != actual:
                raise DictValueMismatchError(path, template, actual)
            return

        regex, fields = compile_template(template, self.pattern_handlers)
        if not fields:
            # No patterns in template, do direct comparison
            if template != actual:
                raise DictValueMismatchError(path, template, actual)
            return

        match = regex.match(actual)
        if not match:
            raise DictPatternMatchError(path, template, actual)

        self._extract_pattern_values(match, fields, path)

    def _extract_pattern_values(self, match, fields, path: str) -> None:
        """Extract and validate pattern values from a regex match."""
        for i, (pattern, identifier) in enumerate(fields, start=1):
            if identifier is None:
                # No identifier, skip checking for consistency
                continue

            matched_value = match.group(i)

            if identifier in self.values[pattern]:
                # If we have seen this identifier on this pattern we just compare the values
                if self.values[pattern][identifier] != matched_value:
                    raise DictPatternValueInconsistencyError(
                        path, identifier, self.values[pattern][identifier], matched_value
                    )
            else:
                # If we have not seen this identifier on this pattern we store the value
                self.values[pattern][identifier] = matched_value
