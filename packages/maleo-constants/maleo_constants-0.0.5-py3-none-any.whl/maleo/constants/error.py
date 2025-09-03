from typing import Dict
from maleo.enums.error import Code as ErrorCode


ERROR_STATUS_CODE_MAP: Dict[ErrorCode, int] = {
    ErrorCode.BAD_REQUEST: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.METHOD_NOT_ALLOWED: 405,
    ErrorCode.CONFLICT: 409,
    ErrorCode.UNPROCESSABLE_ENTITY: 422,
    ErrorCode.TOO_MANY_REQUESTS: 429,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
    ErrorCode.DATABASE_ERROR: 500,
    ErrorCode.NOT_IMPLEMENTED: 501,
    ErrorCode.BAD_GATEWAY: 502,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
}
