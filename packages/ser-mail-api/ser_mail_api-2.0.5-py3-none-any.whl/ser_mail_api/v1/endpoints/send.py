from ser_mail_api.v1.data import Message, Result
from ser_mail_api.v1.resources import Resource


class Send(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)

    def __call__(self, message: Message) -> Result:
        if not isinstance(message, Message):
            raise TypeError(f"Expected 'message' to be an instance of Message, got {type(message).__name__}")
        return Result(self._session.post(self._uri, json=message.to_dict()))
