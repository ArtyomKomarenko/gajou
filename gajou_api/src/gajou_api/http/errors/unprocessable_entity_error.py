from .base_http_error import BaseApiError


class UnprocessableEntityError(BaseApiError):
    def __init__(self, response):
        super().__init__('Unprocessable Entity', response)
