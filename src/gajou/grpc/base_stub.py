from google.protobuf.json_format import MessageToDict, MessageToJson
from grpc import intercept_channel

from .base_interceptor import BaseInterceptor


class BaseStub:
    def __init__(self, channel, stub, allure=None):
        self.channel = intercept_channel(channel, BaseInterceptor(allure))
        self.stub = stub(self.channel)


def response_to_dict(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        return MessageToDict(response)

    return wrapper


def response_to_json(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        return MessageToJson(response)

    return wrapper
