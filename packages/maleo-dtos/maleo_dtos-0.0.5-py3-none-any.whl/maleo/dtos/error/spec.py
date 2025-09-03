from pydantic import BaseModel, Field
from typing import TypeVar
from maleo.enums.error import ErrorType as ErrorTypeEnum
from maleo.mixins.general import StatusCode
from ..descriptor import (
    ErrorDescriptor,
    BadRequestErrorDescriptor,
    UnauthorizedErrorDescriptor,
    ForbiddenErrorDescriptor,
    NotFoundErrorDescriptor,
    MethodNotAllowedErrorDescriptor,
    ConflictErrorDescriptor,
    UnprocessableEntityErrorDescriptor,
    TooManyRequestsErrorDescriptor,
    InternalServerErrorDescriptor,
    DatabaseErrorDescriptor,
    NotImplementedErrorDescriptor,
    BadGatewayErrorDescriptor,
    ServiceUnavailableErrorDescriptor,
)


class ErrorType(BaseModel):
    type: ErrorTypeEnum = Field(
        ErrorTypeEnum.INTERNAL_SERVER_ERROR, description="Error type"
    )


class ErrorSpec(ErrorDescriptor, StatusCode, ErrorType):
    status_code: int = Field(500, description="Status code")


ErrorSpecT = TypeVar("ErrorSpecT", bound=ErrorSpec)


class BadRequestErrorSpec(BadRequestErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.BAD_REQUEST
    status_code: int = 400


class UnauthorizedErrorSpec(UnauthorizedErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.UNAUTHORIZED
    status_code: int = 401


class ForbiddenErrorSpec(ForbiddenErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.FORBIDDEN
    status_code: int = 403


class NotFoundErrorSpec(NotFoundErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.NOT_FOUND
    status_code: int = 404


class MethodNotAllowedErrorSpec(MethodNotAllowedErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.METHOD_NOT_ALLOWED
    status_code: int = 405


class ConflictErrorSpec(ConflictErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.CONFLICT
    status_code: int = 409


class UnprocessableEntityErrorSpec(UnprocessableEntityErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.UNPROCESSABLE_ENTITY
    status_code: int = 422


class TooManyRequestsErrorSpec(TooManyRequestsErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.TOO_MANY_REQUESTS
    status_code: int = 429


class InternalServerErrorSpec(InternalServerErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.INTERNAL_SERVER_ERROR
    status_code: int = 500


class DatabaseErrorSpec(DatabaseErrorDescriptor, InternalServerErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.DATABASE_ERROR


class NotImplementedErrorSpec(NotImplementedErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.NOT_IMPLEMENTED
    status_code: int = 501


class BadGatewayErrorSpec(BadGatewayErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.BAD_GATEWAY
    status_code: int = 502


class ServiceUnavailableErrorSpec(ServiceUnavailableErrorDescriptor, ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.SERVICE_UNAVAILABLE
    status_code: int = 503
