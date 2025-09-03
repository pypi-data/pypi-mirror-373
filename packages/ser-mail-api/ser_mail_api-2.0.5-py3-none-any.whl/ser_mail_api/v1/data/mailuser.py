from __future__ import annotations

import json
import re
from typing import Dict, Optional


class MailUser:
    def __init__(self, email: str, name: Optional[str] = None):
        # Validate email and name types
        if not isinstance(email, str):
            raise TypeError(f"Expected 'email' to be a string, got {type(email).__name__}")
        if name is not None and not isinstance(name, str):
            raise TypeError(f"Expected 'name' to be a string or None, got {type(name).__name__}")

        if not email.strip():
            raise ValueError("Email cannot be empty")

        if not re.match(
                r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)])",
                email, re.IGNORECASE):
            raise ValueError(f"Invalid email format")

        # Set attributes (immutable after initialization)
        self.__email = email
        self.__name = name

    @property
    def email(self) -> str:
        """Get the email address."""
        return self.__email

    @property
    def name(self) -> Optional[str]:
        """Get the display name."""
        return self.__name

    def to_dict(self) -> Dict:
        """Convert the MailUser to a dictionary."""
        data = {
            "email": self.__email,
        }
        if self.__name is not None:
            data["name"] = self.__name

        return data

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)
