import os
import re
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Callable, Any


class ValidationError(Exception):
    """Raised when argument validation fails."""


class PathType:
    """
    Validates that a given path exists (file or directory).
    
    Args:
        mode: "file" → must be a file
              "dir"  → must be a directory
              None   → anything allowed
        must_exist: if False, just returns Path without existence check
    """

    def __init__(self, mode: Optional[str] = None, must_exist: bool = True):
        self.mode = mode
        self.must_exist = must_exist

    def __call__(self, value: str) -> Path:
        path = Path(value)

        if self.must_exist and not path.exists():
            raise ValidationError(f"Path does not exist: {value}")

        if self.mode == "file" and not path.is_file():
            raise ValidationError(f"Expected a file, got: {value}")

        if self.mode == "dir" and not path.is_dir():
            raise ValidationError(f"Expected a directory, got: {value}")

        return path


class EmailType:
    """Validates that a given string is a valid email address."""

    EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

    def __call__(self, value: str) -> str:
        if not self.EMAIL_REGEX.match(value):
            raise ValidationError(f"Invalid email address: {value}")
        return value


class URLType:
    """Validates that a given string is a valid URL."""

    def __call__(self, value: str) -> str:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError(f"Invalid URL: {value}")
        return value


class IntRange:
    """Validate integer within a range."""

    def __init__(self, min_value: Optional[int] = None, max_value: Optional[int] = None):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value: str) -> int:
        try:
            ivalue = int(value)
        except ValueError:
            raise ValidationError("Must be an integer")

        if self.min_value is not None and ivalue < self.min_value:
            raise ValidationError(f"Must be >= {self.min_value}")
        if self.max_value is not None and ivalue > self.max_value:
            raise ValidationError(f"Must be <= {self.max_value}")
        return ivalue


class ChoiceType:
    """Validate input against a set of choices."""

    def __init__(self, choices: list[str], case_sensitive: bool = False):
        self.choices = choices
        self.case_sensitive = case_sensitive

    def __call__(self, value: str) -> str:
        compare = (lambda x: x) if self.case_sensitive else (lambda x: x.lower())

        valid = [compare(c) for c in self.choices]
        if compare(value) not in valid:
            raise ValidationError(f"Must be one of: {', '.join(self.choices)}")
        return value
