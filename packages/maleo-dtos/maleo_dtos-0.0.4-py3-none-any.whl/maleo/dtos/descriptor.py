from pydantic import Field
from maleo.enums.error import Code as ErrorCode
from maleo.enums.success import Code as SuccessCode
from maleo.mixins.general import Descriptor


class ErrorDescriptor(Descriptor[ErrorCode]):
    code: ErrorCode = Field(ErrorCode.INTERNAL_SERVER_ERROR, description="Error's code")
    message: str = Field("Generic Error", description="Error's message")
    description: str = Field(
        "A generic error occurred.", description="Error's description"
    )


class BadRequestErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.BAD_REQUEST
    message: str = "Bad Request"
    description: str = "Bad/Unexpected parameters given."


class UnauthorizedErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.UNAUTHORIZED
    message: str = "Unauthorized"
    description: str = "Authentication is required or invalid."


class ForbiddenErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.FORBIDDEN
    message: str = "Forbidden"
    description: str = "Insufficient permission found."


class NotFoundErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.NOT_FOUND
    message: str = "Not Found"
    description: str = "The requested resource could not be found."


class MethodNotAllowedErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.METHOD_NOT_ALLOWED
    message: str = "Method Not Allowed"
    description: str = "The HTTP method is not supported for this resource."


class ConflictErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.CONFLICT
    message: str = "Conflict"
    description: str = "Failed processing request due to conflicting state."


class UnprocessableEntityErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.UNPROCESSABLE_ENTITY
    message: str = "Unprocessable Entity"
    description: str = "The request was well-formed but could not be processed."


class TooManyRequestsErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.TOO_MANY_REQUESTS
    message: str = "Too Many Requests"
    description: str = "You have sent too many requests in a given time frame."


class InternalServerErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR
    message: str = "Internal Server Error"
    description: str = "An unexpected error occurred on the server."


class DatabaseErrorDescriptor(InternalServerErrorDescriptor):
    code: ErrorCode = ErrorCode.DATABASE_ERROR
    message: str = "Database Error"
    description: str = "An error occurred while accessing the database."


class NotImplementedErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.NOT_IMPLEMENTED
    message: str = "Not Implemented"
    description: str = "This functionality is not supported by the server."


class BadGatewayErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.BAD_GATEWAY
    message: str = "Bad Gateway"
    description: str = (
        "The server received an invalid response from an upstream server."
    )


class ServiceUnavailableErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.SERVICE_UNAVAILABLE
    message: str = "Service Unavailable"
    description: str = "The server is temporarily unable to handle the request."


class SuccessDescriptor(Descriptor[SuccessCode]):
    pass


class AnyDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.ANY_DATA
    message: str = "Any data response"
    description: str = "Response with Any Data"


class NoDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.NO_DATA
    message: str = "No data response"
    description: str = "Response with No Data"


class SingleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.SINGLE_DATA
    message: str = "Single data response"
    description: str = "Response with Single Data"


class CreateSingleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.CREATE_SINGLE_DATA
    message: str = "Create single data response"
    description: str = "Create response with Single Data"


class UpdateSingleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.UPDATE_SINGLE_DATA
    message: str = "Update single data response"
    description: str = "Update response with Single Data"


class OptionalSingleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.OPTIONAL_SINGLE_DATA
    message: str = "Optional single data response"
    description: str = "Response with Optional Single Data"


class ReadSingleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.READ_SINGLE_DATA
    message: str = "Read single data response"
    description: str = "Read response with Single Data"


class DeleteSingleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.DELETE_SINGLE_DATA
    message: str = "Delete single data response"
    description: str = "Delete response with Single Data"


class MultipleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.MULTIPLE_DATA
    message: str = "Multiple data response"
    description: str = "Response with Multiple Data"


class CreateMultipleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.CREATE_MULTIPLE_DATA
    message: str = "Create multiple data response"
    description: str = "Create response with Multiple Data"


class UpdateMultipleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.UPDATE_MULTIPLE_DATA
    message: str = "Update multiple data response"
    description: str = "Update response with Multiple Data"


class OptionalMultipleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.OPTIONAL_MULTIPLE_DATA
    message: str = "Optional multiple data response"
    description: str = "Response with Optional Multiple Data"


class ReadMultipleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.READ_MULTIPLE_DATA
    message: str = "Read multiple data response"
    description: str = "Read response with Multiple Data"


class DeleteMultipleDataSuccessDescriptor(SuccessDescriptor):
    code: SuccessCode = SuccessCode.DELETE_MULTIPLE_DATA
    message: str = "Delete multiple data response"
    description: str = "Delete response with Multiple Data"
