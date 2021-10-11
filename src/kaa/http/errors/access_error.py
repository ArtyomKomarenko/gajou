from .base_http_error import BaseApiError


class AccessError(BaseApiError):
    def __init__(self, response):
        super().__init__('Forbidden', response)
