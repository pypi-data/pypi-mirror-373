"""A package for matching dictionary objects using pattern-based templates."""

from .dict_matcher import DictMatcher
from .exceptions import (
    DictKeyMismatchError,
    DictListLengthMismatchError,
    DictPatternError,
    DictPatternMatchError,
    DictPatternTypeError,
    DictPatternValueInconsistencyError,
    DictStructureError,
    DictValueMismatchError,
)
from .patterns import compile_template

__version__ = "0.2.0"

__all__ = [
    "DictMatcher",
    "compile_template",
    "DictPatternError",
    "DictStructureError",
    "DictKeyMismatchError",
    "DictListLengthMismatchError",
    "DictValueMismatchError",
    "DictPatternMatchError",
    "DictPatternValueInconsistencyError",
    "DictPatternTypeError",
]
