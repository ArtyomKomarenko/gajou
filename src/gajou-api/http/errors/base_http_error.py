from requests import HTTPError


class BaseApiError(HTTPError):
    def __init__(self, label, response):
        msg = f'{response.status_code} {label} Error for {response.url}'
        if response.text != '':
            msg = f'{msg}: {response.text}'
        super().__init__(msg, response=response)

    def body(self):
        try:
            return self.response.json()
        except ValueError:
            return self.response.text

    def reason(self):
        if isinstance(self.response.reason, bytes):
            try:
                reason = self.response.reason.decode('utf-8')
            except UnicodeDecodeError:
                reason = self.response.reason.decode('iso-8859-1')
        else:
            reason = self.response.reason
        return reason
