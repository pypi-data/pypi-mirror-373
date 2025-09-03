from ser_mail_api.v1.resources import Dictionary


class Result(Dictionary):
    @property
    def message_id(self) -> str:
        return self.get('message_id')

    @property
    def reason(self) -> str:
        return self.get('reason')

    @property
    def request_id(self) -> str:
        return self.get('request_id')
