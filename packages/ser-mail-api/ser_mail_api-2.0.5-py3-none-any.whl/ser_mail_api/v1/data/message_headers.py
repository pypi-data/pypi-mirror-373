from .mailuser import MailUser


class MessageHeaders:
    def __init__(self, header_from: MailUser):
        if not isinstance(header_from, MailUser):
            raise TypeError(f"Expected header from to be a MailUser, got {type(header_from).__name__}")

        self.__header_from = header_from

    @property
    def header_from(self) -> MailUser:
        return self.__header_from

    @header_from.setter
    def header_from(self, header_from: MailUser):
        if not isinstance(header_from, MailUser):
            raise TypeError(f"Expected header_from to be a MailUser, got {type(header_from).__name__}")
        self.__header_from = header_from

    def to_dict(self):
        return {
            'from': self.header_from.to_dict()
        }
