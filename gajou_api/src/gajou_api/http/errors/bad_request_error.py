from .base_http_error import BaseApiError


class BadRequestError(BaseApiError):
    def __init__(self, response):
        super().__init__('Bad Request', response)
