from enum import StrEnum


class ErrorType(StrEnum):
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


class Code(StrEnum):
    BAD_REQUEST = "MAL-ERR-CLI-BDR-001"
    UNAUTHORIZED = "MAL-ERR-CLI-ATH-001"
    FORBIDDEN = "MAL-ERR-CLI-FBD-001"
    NOT_FOUND = "MAL-ERR-CLI-NTF-001"
    METHOD_NOT_ALLOWED = "MAL-ERR-CLI-MNA-001"
    CONFLICT = "MAL-ERR-CLI-CFL-001"
    UNPROCESSABLE_ENTITY = "MAL-ERR-CLI-UPE-001"
    TOO_MANY_REQUESTS = "MAL-ERR-CLI-TMR-001"
    INTERNAL_SERVER_ERROR = "MAL-ERR-SRV-ISE-001"
    DATABASE_ERROR = "MAL-ERR-SRV-ISE-002"
    NOT_IMPLEMENTED = "MAL-ERR-SRV-NIM-001"
    BAD_GATEWAY = "MAL-ERR-SRV-BDG-001"
    SERVICE_UNAVAILABLE = "MAL-ERR-SRV-SUN-001"
