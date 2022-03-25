from .base_http_error import BaseApiError


class ServerError(BaseApiError):
    def __init__(self, response):
        super().__init__('Server', response)
