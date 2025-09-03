import json
from typing import List, Dict, Optional

from .attachment import Attachment
from .content import Content
from .mailuser import MailUser
from .message_headers import MessageHeaders


class Message:
    def __init__(self, subject: str, sender: MailUser, header_from: Optional[MailUser] = None):
        if not isinstance(sender, MailUser):
            raise TypeError(f"Expected sender to be a MailUser, got {type(sender).__name__}")
        if header_from is not None and not isinstance(header_from, MailUser):
            raise TypeError(f"Expected header_from to be a MailUser or None, got {type(header_from).__name__}")
        if not isinstance(subject, str):
            raise TypeError(f"Expected subject to be a string, got {type(subject).__name__}")

        self.__subject = subject
        self.__sender = sender
        self.__headers = None
        if header_from is not None:
            self.header_from = header_from
        self.__to: List[MailUser] = []
        self.__cc: List[MailUser] = []
        self.__bcc: List[MailUser] = []
        self.__reply_tos: List[MailUser] = []
        self.__attachments: List[Attachment] = []
        self.__content: List[Content] = []

    @property
    def sender(self) -> MailUser:
        return self.__sender

    @sender.setter
    def sender(self, sender: MailUser):
        if not isinstance(sender, MailUser):
            raise TypeError(f"Expected sender to be a MailUser, got {type(sender).__name__}")
        self.__sender = sender

    @property
    def header_sender(self) -> Optional[MailUser]:
        return self.header_from

    @header_sender.setter
    def header_sender(self, sender: MailUser):
        self.header_from = sender

    @property
    def header_from(self) -> Optional[MailUser]:
        return self.__headers.header_from if self.__headers else None

    @header_from.setter
    def header_from(self, header_from: Optional["MailUser"]):
        if header_from is None:
            self.__headers = None
        elif self.__headers is None:
            self.__headers = MessageHeaders(header_from)
        else:
            self.__headers.From = header_from

    @property
    def headers(self) -> Optional[MessageHeaders]:
        return self.__headers

    @headers.setter
    def headers(self, headers: Optional[MessageHeaders] = None):
        if headers is not None and not isinstance(headers, MessageHeaders):
            raise TypeError(f"Expected headers to be a MessageHeaders, got {type(headers).__name__}")
        self.__headers = headers

    def add_to(self, to_user: MailUser):
        if not isinstance(to_user, MailUser):
            raise TypeError(f"Expected to_user to be a MailUser, got {type(to_user).__name__}")
        self.__to.append(to_user)

    def add_cc(self, cc_user: MailUser):
        if not isinstance(cc_user, MailUser):
            raise TypeError(f"Expected cc_user to be a MailUser, got {type(cc_user).__name__}")
        self.__cc.append(cc_user)

    def add_bcc(self, bcc_user: MailUser):
        if not isinstance(bcc_user, MailUser):
            raise TypeError(f"Expected bcc_user to be a MailUser, got {type(bcc_user).__name__}")
        self.__bcc.append(bcc_user)

    def add_reply_to(self, reply_to_user: MailUser):
        if not isinstance(reply_to_user, MailUser):
            raise TypeError(f"Expected reply_to_user to be a MailUser, got {type(reply_to_user).__name__}")
        self.__reply_tos.append(reply_to_user)

    def add_attachment(self, attachment: Attachment):
        if not isinstance(attachment, Attachment):
            raise TypeError(f"Expected attachment to be an Attachment, got {type(attachment).__name__}")
        self.__attachments.append(attachment)

    def add_content(self, content: Content):
        if not isinstance(content, Content):
            raise TypeError(f"Expected content to be a Content, got {type(content).__name__}")
        self.__content.append(content)

    def to_dict(self) -> Dict:
        data = {
            "from": self.__sender.to_dict(),
            "subject": self.__subject,
        }
        if self.__content:
            data['content'] = [content.to_dict() for content in self.__content]

        if self.__headers is not None:
            data['headers'] = self.__headers.to_dict()

        if self.__to:
            data['tos'] = [recipient.to_dict() for recipient in self.__to]

        if self.__cc:
            data['cc'] = [cc_user.to_dict() for cc_user in self.__cc]

        if self.__bcc:
            data['bcc'] = [bcc_user.to_dict() for bcc_user in self.__bcc]

        if self.__reply_tos:
            data['replyTos'] = [reply_to_user.to_dict() for reply_to_user in self.__reply_tos]

        if self.__attachments:
            data['attachments'] = [attachment.to_dict() for attachment in self.__attachments]

        return data

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)
