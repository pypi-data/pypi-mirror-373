r"""
Pattern compilation utilities for dictionary pattern matching.

This module provides functionality to compile template strings containing
pattern placeholders into regular expressions that can be used for matching
and extracting values from strings.

Pattern placeholders follow the format: {pattern_name:identifier}
where pattern_name is the type of pattern to match, and identifier is
an optional name for the captured value.

Examples
--------
>>> available_patterns = {'string': r'[a-zA-Z]+', 'number': r'\\d+'}
>>> template = "Hello {string:name}, you are {number:age} years old"
>>> regex, fields = compile_template(template, available_patterns)
>>> match = regex.match("Hello John, you are 25 years old")
>>> if match:
...     print(fields)  # [('string', 'name'), ('number', 'age')]
...     print(match.group(1))  # 'John'
...     print(match.group(2))  # '25'

"""

import re

from .exceptions import DictPatternTypeError

MASTER_PATTERN_REGEX = re.compile(r"\{(?P<pattern>[a-z_]+)(?::(?P<identifier>[a-zA-Z0-9_]+))?\}")


def compile_template(template: str, available_patterns: dict) -> tuple[re.Pattern, list[tuple[str, str]]]:
    r"""
    Convert a template with placeholders into a regex and metadata.

    This function takes a template string containing pattern placeholders
    and compiles it into a regular expression that can be used for matching.
    It also returns metadata about the captured groups for later processing.

    Parameters
    ----------
    template : str
        The template string containing pattern placeholders in the format
        {pattern_name:identifier}. The identifier part is optional.
        Example: "Hello {string:name}, you are {number:age} years old"
    available_patterns : dict
        Dictionary mapping pattern names to their corresponding regex patterns.
        The regex patterns should not include capturing groups as they will
        be automatically wrapped in parentheses.
        Example: {'string': r'[a-zA-Z]+', 'number': r'\\d+'}

    Returns
    -------
    tuple[re.Pattern, list[tuple[str, str]]]
        A tuple containing:
        - A compiled regular expression that matches the template
        - A list of tuples, each containing (pattern_name, identifier) for
          each placeholder found in the template. If no identifier was
          provided, the second element will be None.

    Raises
    ------
    ValueError
        If a pattern name in the template is not found in available_patterns.

    Examples
    --------
    >>> patterns = {'word': r'\\w+', 'digit': r'\\d+'}
    >>> template = "User {word:username} has {digit:score} points"
    >>> regex, fields = compile_template(template, patterns)
    >>>
    >>> # The regex will match strings like "User john123 has 42 points"
    >>> match = regex.match("User john123 has 42 points")
    >>> match is not None
    True
    >>>
    >>> # Fields contain the pattern and identifier information
    >>> fields
    [('word', 'username'), ('digit', 'score')]
    >>>
    >>> # Captured groups can be accessed
    >>> match.group(1)  # username value
    'john123'
    >>> match.group(2)  # score value
    '42'

    Notes
    -----
    - The returned regex is anchored to the start and end of the string (^...$)
    - Literal text between placeholders is automatically escaped
    - Each placeholder becomes a capturing group in the regex
    - The order of capturing groups matches the order of placeholders in the template

    """
    regex_parts = []
    last_end = 0
    fields = []  # to keep track of (pattern, identifier)

    for match in MASTER_PATTERN_REGEX.finditer(template):
        pattern = match.group("pattern")
        identifier = match.group("identifier")

        # Add literal text before this placeholder
        regex_parts.append(re.escape(template[last_end : match.start()]))

        if pattern not in available_patterns:
            raise DictPatternTypeError(pattern, list(available_patterns.keys()))

        # Add the capturing group for this placeholder
        regex_parts.append(f"({available_patterns[pattern]})")

        # Remember mapping of this group
        fields.append((pattern, identifier))

        last_end = match.end()

    # Add any remaining text, as literal, after last placeholder
    regex_parts.append(re.escape(template[last_end:]))

    # Compile regex
    full_regex = "".join(regex_parts)
    return re.compile(f"^{full_regex}$"), fields
