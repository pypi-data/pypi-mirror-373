"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from abc import ABC, abstractmethod


class Parameter(ABC):
    @abstractmethod
    def __str__(self) -> str:
        """
        Format the parameter as a string suitable for URI or POST data.
        """
        pass
