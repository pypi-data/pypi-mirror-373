from enum import StrEnum


class Error(StrEnum):
    BAD_REQUEST = "client.bad_request"
    UNAUTHORIZED = "client.unauthorized"
    FORBIDDEN = "client.forbidden"
    NOT_FOUND = "client.not_found"
    CONFLICT = "client.conflict"
    METHOD_NOT_ALLOWED = "client.method_not_allowed"
    UNPROCESSABLE_ENTITY = "client.unprocessable_entity"
    TOO_MANY_REQUESTS = "client.too_many_requests"
    INTERNAL_SERVER_ERROR = "server.internal_server_error"
    DATABASE_ERROR = "server.internal_server_error.database_error"
    NOT_IMPLEMENTED = "server.not_implemented"
    BAD_GATEWAY = "server.bad_gateway"
    SERVICE_UNAVAILABLE = "server.service_unavailable"
