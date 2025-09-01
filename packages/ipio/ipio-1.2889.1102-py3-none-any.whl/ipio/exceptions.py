class SetDatetimeException(Exception):
    pass


class ConfigNotSetException(Exception):
    pass


class InvalidIPException(Exception):
    pass


class MutedSystemException(Exception):
    pass


class EmptyParamsException(Exception):
    pass


class UnusableSocketException(Exception):
    pass


class MessageSizeException(Exception):
    pass


class AuthenticationException(Exception):
    pass


class AuthorizationException(Exception):
    pass


class CommunicationException(Exception):
    """Base class for communication-related errors"""

    pass
