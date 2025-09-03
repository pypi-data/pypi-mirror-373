"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from __future__ import annotations

from typing import Dict, TypeVar, Optional, Callable

from requests import Response

from .response_wrapper import ResponseWrapper


class Dictionary(Dict, ResponseWrapper):
    """
    A specialized dictionary that wraps an HTTP response, providing access to both
    the JSON data (as a dictionary) and the original response object.
    """

    def __init__(self, response: Response, transform: Optional[Callable[[Response], Dict]] = None):
        """
        Initializes the Dictionary with JSON data from an HTTP response.

        Args:
            response (Response): The HTTP response object.
            transform (Callable[[Response], Dict], optional): A function to transform the response into
                a dictionary. Defaults to None.

        Raises:
            ValueError: If the response body is not valid JSON.
        """
        try:
            ResponseWrapper.__init__(self, response)
            # Apply the transform function if provided, otherwise use response.json()
            if transform is not None:
                if not callable(transform):
                    raise TypeError("`transform` must be a callable function.")
                transformed_data = transform(response)
                if not isinstance(transformed_data, dict):
                    raise ValueError("`transform` function must return a dictionary.")
                super().__init__(transformed_data)
            else:
                super().__init__(response.json())
        except ValueError as e:
            raise ValueError(
                f"Malformed JSON response from request. HTTP [{response.status_code}/{response.reason}] - {response.text[:255]}") from e


TDictionary = TypeVar('TDictionary', bound=Dictionary)
