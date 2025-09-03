"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from typing import Any

from requests import Response

ERROR_MESSAGES = {
    400: "Bad Request",
    401: "Unauthorized",
    404: "Not Found",
    405: "Method Not Allowed",
    413: "Payload Too Large",
    415: "Unsupported Media Type for Request",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    503: "Service Unavailable",
}


class ErrorHandler:
    """
    A class to handle HTTP responses, providing custom error messages for specific status codes
    and optionally raising exceptions for non-successful responses.

    Attributes:
        raise_for_status (bool): Whether to raise an exception for non-successful HTTP responses.

    Methods:
        handler(response: Response, *args, **kwargs) -> Response:
            Processes the response, sets custom error messages, and optionally raises exceptions.
    """

    def __init__(self, raise_for_status: bool = False):
        """
        Initializes the ErrorHandler.

        Args:
            raise_for_status (bool): Whether to raise exceptions for non-successful HTTP responses. Defaults to False.
        """
        self.__raise_for_status: bool = raise_for_status

    def handler(self, response: Response, *args: Any, **kwargs: Any) -> Response:
        """
        Processes the HTTP response, sets custom error messages for specific status codes,
        and optionally raises exceptions for non-successful responses.

        Args:
            response (Response): The HTTP response object.
            *args: Additional positional arguments (ignored).
            **kwargs: Additional keyword arguments (ignored).

        Returns:
            Response: The processed HTTP response object.
        """
        if response.status_code in ERROR_MESSAGES:
            response.reason = ERROR_MESSAGES[response.status_code]

        if self.__raise_for_status:
            response.raise_for_status()

        return response

    @property
    def raise_for_status(self) -> bool:
        """Gets whether exceptions are raised for non-successful responses."""
        return self.__raise_for_status

    @raise_for_status.setter
    def raise_for_status(self, raise_for_status: bool):
        """Sets whether exceptions are raised for non-successful responses."""
        self.__raise_for_status = raise_for_status
