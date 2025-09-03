"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from __future__ import annotations

from typing import Type, Generic, Union

from .dictionary import Dictionary, TDictionary
from .resource import Resource


class DictionaryResource(Generic[TDictionary], Resource):
    """
    Represents a resource that maps to a dictionary-like object.

    Attributes:
        _dict_type (Type[TDictionary]): The type of dictionary to use for resource data.
    """

    def __init__(self, parent: Union[Resource, None], uri: str, dict_type: Type[TDictionary] = Dictionary):
        """
        Initializes a new DictionaryResource.

        Args:
            parent (Resource): The parent resource.
            uri (str): The name/URI segment for this resource.
            dict_type (Type[TDictionary]): The dictionary type to use for resource data. Defaults to `Dictionary`.
        """
        super().__init__(parent, uri)
        self._dict_type = dict_type

    def __call__(self) -> TDictionary:
        """
        Fetches the resource data and returns it as an instance of the dictionary type.

        Returns:
            TDictionary: An instance of the dictionary type containing the resource data.

        Raises:
            requests.exceptions.RequestException: If the HTTP request fails.
            ValueError: If the response data cannot be converted to the specified dictionary type.
        """
        try:
            return self._dict_type(self._session.get(self._uri))
        except Exception as e:
            raise ValueError(f"Failed to fetch or parse resource data from {self._uri}: {e}")
