from __future__ import annotations

import base64
import json
import mimetypes
import os
import uuid
from enum import Enum
from typing import Dict, Optional


def _deduce_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        raise ValueError(f"Unable to deduce MIME type for file: {file_path}")
    return mime_type


def _encode_file_content(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def _is_valid_base64(s: str) -> bool:
    try:
        return base64.b64encode(base64.b64decode(s)).decode('utf-8') == s
    except Exception:
        return False


class Disposition(Enum):
    Inline = "inline"
    Attachment = "attachment"


class Attachment:
    def __init__(self, content: str, filename: str, mime_type: Optional[str] = None,
                 disposition: Disposition = Disposition.Attachment, cid: Optional[str] = None):
        """
        Args:
            content (str): base64 encoded content.
            filename (str): Filename of the attachment.
            mime_type (str): MIME type of the content. If None, it will try to deduce it from the filename.
            disposition (Disposition): The disposition of the attachment (inline or attachment).
            cid (Optional[str]): The Content-ID of the attachment. If not specified, for an inline attachment the value will be a random UUID.
        """

        # Validate input types
        if not isinstance(content, str):
            raise TypeError(f"Expected 'content' to be a string, got {type(content).__name__}")
        if not isinstance(disposition, Disposition):
            raise TypeError(f"Expected 'disposition' to be a Disposition, got {type(disposition).__name__}")
        if not isinstance(filename, str):
            raise TypeError(f"Expected 'filename' to be a string, got {type(filename).__name__}")

        if mime_type is not None and not isinstance(mime_type, str):
            raise TypeError(f"Expected 'mime_type' to be a string, got {type(mime_type).__name__}")

        # Validate specific constraints
        if not _is_valid_base64(content):
            raise ValueError("Invalid Base64 content")

        if not filename.strip():
            raise ValueError("Filename must be a non-empty string")

        if len(filename) > 1000:
            raise ValueError("Filename must be at most 1000 characters long")

        # User provided mime_type or try to deduce it from filename
        if mime_type is None:
            mime_type = _deduce_mime_type(filename)

        if not mime_type.strip():
            raise ValueError("Mime type must be a non-empty string")

        # Covers None, empty string, or whitespace-only strings
        if not cid or cid.isspace():
            self.__cid = str(uuid.uuid4())  # Generate a UUID
        elif isinstance(cid, str):
            self.__cid = cid  # Use provided string
        else:
            raise TypeError(f"Expected 'cid' to be a string or None, got {type(cid).__name__}")

        # CID only applies to inline attachments
        if disposition == Disposition.Attachment:
            self.__cid = None

        self.__content = content
        self.__disposition = disposition
        self.__filename = filename
        self.__mime_type = mime_type

    @property
    def id(self) -> str:
        return self.__cid

    @property
    def cid(self) -> str:
        return self.__cid

    @property
    def content(self) -> str:
        return self.__content

    @property
    def disposition(self) -> Disposition:
        return self.__disposition

    @property
    def filename(self) -> str:
        return self.__filename

    @property
    def mime_type(self) -> str:
        return self.__mime_type

    def to_dict(self) -> Dict:
        data = {
            "content": self.__content,
            "disposition": self.__disposition.value,
            "filename": self.__filename,
            "type": self.__mime_type,
        }

        if self.disposition == Disposition.Inline:
            data["id"] = self.__cid

        return data

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    @staticmethod
    def from_base64(base64string: str, filename: str, mime_type: Optional[str] = None,
                    disposition: Disposition = Disposition.Attachment, cid: Optional[str] = None) -> Attachment:
        """
        Args:
            base64string (str): base64 encoded content.
            filename (str): Filename of the attachment.
            mime_type (Optional[str]): MIME type of the content. If None, it will try to deduce it from the filename.
            disposition (Disposition): The disposition of the attachment (inline or attachment).
            cid (Optional[str]): The Content-ID of the attachment. If not specified, for an inline attachment the value will be a random UUID.
        """
        return Attachment(base64string, filename, mime_type, disposition, cid)

    @staticmethod
    def from_file(file_path: str, disposition: Disposition = Disposition.Attachment, cid: Optional[str] = None,
                  filename: Optional[str] = None, mime_type: Optional[str] = None) -> Attachment:
        """
        Args:
            file_path (str): Path to the file.
            disposition (Disposition): The disposition of the attachment (inline or attachment).
            cid (Optional[str]): The Content-ID of the attachment. If not specified, for an inline attachment the value will be a random UUID.
            filename (Optional[str]): Overrides the filename. Defaults to deriving from file_path.
            mime_type (Optional[str]): Overrides the MIME type. Defaults to None, and will be deduced by the Attachment object by filename.
        """
        if not isinstance(file_path, str):
            raise TypeError(f"Expected 'file_path' to be a string, got {type(file_path).__name__}")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file at path '{file_path}' does not exist.")

        # Allow filename override
        if filename is None:
            filename = os.path.basename(file_path)

        # Encode file content
        content = _encode_file_content(file_path)

        return Attachment(content, filename, mime_type, disposition, cid)

    @staticmethod
    def from_bytes(data: bytes, filename: str, mime_type: Optional[str] = None, disposition: Disposition = Disposition.Attachment,
                   cid: Optional[str] = None) -> Attachment:
        """
        Args:
            data (bytes): Byte array of the content.
            filename (str): Filename of the attachment.
            mime_type (Optional[str]): MIME type of the content. If None, it will try to deduce it from the filename.
            disposition (Disposition): The disposition of the attachment (inline or attachment).
            cid (Optional[str]): The Content-ID of the attachment. If not specified, for an inline attachment the value will be a random UUID.
        """
        if not isinstance(data, bytes):
            raise TypeError(f"Expected 'data' to be bytes, got {type(data).__name__}")

        # Encode byte array to Base64
        content = base64.b64encode(data).decode("utf-8")

        return Attachment(content, filename, mime_type, disposition, cid)
