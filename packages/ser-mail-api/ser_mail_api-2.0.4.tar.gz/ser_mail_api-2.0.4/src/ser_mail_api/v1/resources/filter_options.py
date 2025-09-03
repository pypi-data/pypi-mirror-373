"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from datetime import datetime
from enum import Enum
from typing import TypeVar, Dict, Any

from .parameter import Parameter


class FilterOptions:
    _options: Dict[str, Any]

    def __init__(self):
        self._options = {}

    def clear(self) -> None:
        """
        Clears all options.
        """
        self._options.clear()

    def add_option(self, key: str, value: Any) -> None:
        """
        Adds a key-value pair to the options with validation.

        Args:
            key (str): The option key.
            value (Any): The option value.

        Raises:
            TypeError: If the value type is not supported.
        """
        if value is None:
            return

        if not isinstance(value, (str, list, datetime, Enum, int, float, bool, Parameter)):
            raise TypeError(f"Unsupported type for option value: {type(value).__name__}")
        self._options[key] = value

    def _format_value(self, key: str, value: Any) -> str:
        """
        Formats a single value based on its type for query parameters.

        Args:
            key (str): The key for the parameter.
            value: The value to format.

        Returns:
            str: The formatted value as a string.
        """
        if isinstance(value, Parameter):
            return f"{key}={str(value)}"
        elif isinstance(value, list) and value:
            if all(isinstance(n, str) for n in value):
                return f"{key}=[{','.join(value)}]"
            elif all(isinstance(n, Enum) for n in value):
                return f"{key}=[{','.join(n.value for n in value)}]"
        elif isinstance(value, datetime):
            return f"{key}={value.strftime('%Y-%m-%dT%H:%M:%S')}"
        elif isinstance(value, Enum):
            return f"{key}={value.value}"
        else:
            return f"{key}={value}"

    def __str__(self) -> str:
        """
        Converts the options into a query string.

        Returns:
            str: The formatted query string.
        """
        return "&".join(
            self._format_value(k, v) for k, v in self._options.items() if v is not None
        )

    @property
    def params(self) -> Dict[str, Any]:
        """
        Converts the options into a dictionary format suitable for HTTP requests.

        Returns:
            Dict[str, Any]: The formatted parameters as a dictionary.
        """
        result = {}
        for k, v in self._options.items():
            if isinstance(v, Parameter):
                result[k] = str(v)
            elif isinstance(v, list) and v:
                if all(isinstance(n, str) for n in v):
                    result[k] = f"[{','.join(v)}]"
                elif all(isinstance(n, Enum) for n in v):
                    result[k] = f"[{','.join(n.value for n in v)}]"
            elif isinstance(v, datetime):
                result[k] = v.strftime('%Y-%m-%dT%H:%M:%S')
            elif isinstance(v, Enum):
                result[k] = v.value
            else:
                result[k] = v
        return result


TFilterOptions = TypeVar("TFilterOptions", bound=FilterOptions)
