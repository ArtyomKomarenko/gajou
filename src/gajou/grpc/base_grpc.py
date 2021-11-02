from typing import List

from grpc import insecure_channel, intercept_channel, secure_channel, ssl_channel_credentials

from .base_interceptor import BaseInterceptor


class BaseGRPC:
    def __init__(self, host, port, stub, secure, client_interceptors: List = None, allure=None):
        if secure:
            channel = secure_channel(f'{host}:{port}', ssl_channel_credentials())
        else:
            channel = insecure_channel(f'{host}:{port}')

        interceptors = [BaseInterceptor(allure)]
        if isinstance(client_interceptors, list):
            interceptors.extend(client_interceptors)

        self.channel = intercept_channel(channel, *interceptors)
        self.stub = stub(self.channel)
