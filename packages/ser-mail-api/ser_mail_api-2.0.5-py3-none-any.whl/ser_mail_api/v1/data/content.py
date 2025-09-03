from __future__ import annotations

import json
from enum import Enum
from typing import Dict


class ContentType(Enum):
    Text = "text/plain"
    Html = "text/html"


class Content:
    def __init__(self, body: str, content_type: ContentType):
        # Validate body and content_type types
        if not isinstance(body, str):
            raise TypeError(f"Expected 'body' to be a string, got {type(body).__name__}")
        if not isinstance(content_type, ContentType):
            raise TypeError(f"Expected 'content_type' to be a ContentType, got {type(content_type).__name__}")

        # Set attributes (immutable after initialization)
        self.__body = body
        self.__content_type = content_type

    @property
    def body(self) -> str:
        """Get the content body."""
        return self.__body

    @property
    def type(self) -> ContentType:
        """Get the content type."""
        return self.__content_type

    def to_dict(self) -> Dict:
        """Convert the Content object to a dictionary."""
        return {
            "body": self.__body,
            "type": self.__content_type.value,
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)
