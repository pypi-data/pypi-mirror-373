from enum import StrEnum


class ErrorCode(StrEnum):
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    ARGUMENT_ERROR = "ARGUMENT_ERROR"
    NO_MEMBERSHIP = "NO_MEMBERSHIP"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    ALREADY_EXISTS = "ALREADY_EXISTS"


class DisplayMessage(StrEnum):
    UNKNOWN_ERROR = "errors.unknownError"
    NOT_AUTHENTICATED = "errors.notAuthenticated"
    NOT_FOUND = "errors.notFound"
    BAD_REQUEST = "errors.badRequest"
    ARGUMENT_ERROR = "errors.argumentError"
    PERMISSION_DENIED = "errors.noPermission"
    NO_MEMBERSHIP = "errors.noMembership"
    ALREADY_EXISTS = "errors.alreadyExists"


class SKU(StrEnum):
    SYNCED_VACANCY = 'synced_vacancy'

