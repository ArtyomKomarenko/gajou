from grpc import StatusCode


class GRPCError(Exception):
    def __init__(self, status_code: StatusCode, details):
        self.status_code = status_code
        self.details = details
