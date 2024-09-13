class HarmonizeException(Exception):
    """
    Base class for Harmonize exceptions.

    Tip
    ---
        When catching errors, you can use this error class without using all other error classes
    """


class AuthorizationError(HarmonizeException):
    """
    Represents an authorization error. Throws when authorization fails.
    """


class NodeUnknownError(HarmonizeException):
    """
    Represents a node unknown error. Throws at 404 status.
    """


class Forbidden(HarmonizeException):
    """
    Represents an authentication error. Throws when authorization fails or forbidden status
    """

    def __init__(self, name: str) -> None:
        super().__init__(f"The node {name} is forbidden")


class InvalidData(HarmonizeException):
    """
    Represents an invalid data error. Throws when data is not valid.
    """


class InvalidSession(HarmonizeException):
    """
    Represents an invalid session error. Throws when session is not valid.
    """


class RequestError(HarmonizeException):
    """
    Represents a request error. Throws when the request fails.
    """


class InvalidChannelStateException(HarmonizeException):
    """
    Represents an invalid channel state error. Throws when trying to move a player without a valid guild or channel.
    """
