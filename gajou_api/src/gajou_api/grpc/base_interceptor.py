import logging

from google.protobuf.json_format import MessageToDict
from grpc import (RpcError,
                  StreamUnaryClientInterceptor, StreamStreamClientInterceptor,
                  UnaryUnaryClientInterceptor, UnaryStreamClientInterceptor)

from .grpc_error import GRPCError


class BaseInterceptor(UnaryUnaryClientInterceptor, UnaryStreamClientInterceptor,
                      StreamUnaryClientInterceptor, StreamStreamClientInterceptor):
    def __init__(self, allure):
        self.allure = allure
        self.logger = logging.getLogger(__name__)

    def _intercept(self, continuation, client_call_details, request_or_iterator):
        self._log_request(client_call_details.method, request_or_iterator)

        response = continuation(client_call_details, request_or_iterator)

        self._raise_for_status(response)
        self._log_response(response)

        return response

    def _log_request(self, method, data):
        body = MessageToDict(data)
        self.logger.info(f'gRPC {method} {body}')
        if self.allure:
            self.allure.attach(f'{method} {body}', 'Request', self.allure.attachment_type.TEXT)

    def _log_response(self, response):
        body = MessageToDict(response.result())
        self.logger.info(f'Response: {body}')
        if self.allure:
            self.allure.attach(f'{body}', 'Response', self.allure.attachment_type.TEXT)

    def _raise_for_status(self, response):
        if not isinstance(response, RpcError):
            return
        self.logger.info(f'Response status: {response.code().name}, message: `{response.details()}`')
        if self.allure:
            self.allure.attach(response.details(), 'Error', self.allure.attachment_type.TEXT)
        raise GRPCError(status_code=response.code(), details=response.details())

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept(continuation, client_call_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        return self._intercept(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return self._intercept(continuation, client_call_details, request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        return self._intercept(continuation, client_call_details, request_iterator)
