class HarmonizeException(Exception):
    """Base exception class"""


class AuthorizationError(HarmonizeException):
    pass


class NodeUnknownError(HarmonizeException):
    pass


class AuthenticationError(HarmonizeException):
    def __init__(self, name: str) -> None:
        super().__init__("Node " + name + " isn\'t authorized")


class InvalidData(HarmonizeException):
    pass


class ClientError(HarmonizeException):
    pass


class RequestError(HarmonizeException):
    pass


class InvalidChannelStateException(HarmonizeException):
    pass
