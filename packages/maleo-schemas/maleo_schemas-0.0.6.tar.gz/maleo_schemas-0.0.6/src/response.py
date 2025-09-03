from pydantic import BaseModel, Field
from typing import Dict, Generic, List, Literal, Optional, Type, TypeVar, Union
from maleo.dtos.data import DataPair, GenericDataT, DataT
from maleo.dtos.descriptor import (
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
    SuccessDescriptor,
    AnyDataSuccessDescriptor,
    NoDataSuccessDescriptor,
    SingleDataSuccessDescriptor,
    OptionalSingleDataSuccessDescriptor,
    CreateSingleDataSuccessDescriptor,
    ReadSingleDataSuccessDescriptor,
    UpdateSingleDataSuccessDescriptor,
    DeleteSingleDataSuccessDescriptor,
    MultipleDataSuccessDescriptor,
    OptionalMultipleDataSuccessDescriptor,
    CreateMultipleDataSuccessDescriptor,
    ReadMultipleDataSuccessDescriptor,
    UpdateMultipleDataSuccessDescriptor,
    DeleteMultipleDataSuccessDescriptor,
)
from maleo.dtos.metadata import MetadataT
from maleo.dtos.pagination import PaginationT, GenericPaginationT
from maleo.dtos.payload import (
    Payload,
    NoDataPayload,
    SingleDataPayload,
    CreateSingleDataPayload,
    ReadSingleDataPayload,
    UpdateSingleDataPayload,
    DeleteSingleDataPayload,
    OptionalSingleDataPayload,
    MultipleDataPayload,
    CreateMultipleDataPayload,
    ReadMultipleDataPayload,
    UpdateMultipleDataPayload,
    DeleteMultipleDataPayload,
    OptionalMultipleDataPayload,
)
from maleo.enums.error import Code as ErrorCode
from maleo.enums.success import Code as SuccessCode
from maleo.mixins.general import SuccessT, Success, CodeT, Descriptor
from maleo.types.base.any import OptionalAny


class Response(
    Payload[GenericDataT, GenericPaginationT, MetadataT],
    Descriptor[CodeT],
    Success[SuccessT],
    BaseModel,
    Generic[SuccessT, CodeT, GenericDataT, GenericPaginationT, MetadataT],
):
    pass


ResponseT = TypeVar("ResponseT", bound=Response)


class ResponseMixin(BaseModel, Generic[ResponseT]):
    response: ResponseT = Field(..., description="Response")


# Failure Response
class ErrorResponse(
    NoDataPayload[None],
    ErrorDescriptor,
    Response[Literal[False], ErrorCode, None, None, None],
):
    success: Literal[False] = False
    data: None = None
    pagination: None = None
    metadata: None = None
    other: OptionalAny = "Please try again later or contact administrator"


ErrorResponseT = TypeVar("ErrorResponseT", bound=ErrorResponse)


class BadRequestResponse(
    BadRequestErrorDescriptor,
    ErrorResponse,
):
    pass


class UnauthorizedResponse(
    UnauthorizedErrorDescriptor,
    ErrorResponse,
):
    pass


class ForbiddenResponse(
    ForbiddenErrorDescriptor,
    ErrorResponse,
):
    pass


class NotFoundResponse(
    NotFoundErrorDescriptor,
    ErrorResponse,
):
    pass


class MethodNotAllowedResponse(
    MethodNotAllowedErrorDescriptor,
    ErrorResponse,
):
    pass


class ConflictResponse(
    ConflictErrorDescriptor,
    ErrorResponse,
):
    pass


class UnprocessableEntityResponse(
    UnprocessableEntityErrorDescriptor,
    ErrorResponse,
):
    pass


class TooManyRequestsResponse(
    TooManyRequestsErrorDescriptor,
    ErrorResponse,
):
    pass


class InternalServerErrorResponse(
    InternalServerErrorDescriptor,
    ErrorResponse,
):
    pass


class DatabaseErrorResponse(
    DatabaseErrorDescriptor,
    ErrorResponse,
):
    pass


class NotImplementedResponse(
    NotImplementedErrorDescriptor,
    ErrorResponse,
):
    pass


class BadGatewayResponse(
    BadGatewayErrorDescriptor,
    ErrorResponse,
):
    pass


class ServiceUnavailableResponse(
    ServiceUnavailableErrorDescriptor,
    ErrorResponse,
):
    pass


ERROR_RESPONSE_MAP: Dict[ErrorCode, Type[ErrorResponse]] = {
    ErrorCode.BAD_REQUEST: BadRequestResponse,
    ErrorCode.UNAUTHORIZED: UnauthorizedResponse,
    ErrorCode.FORBIDDEN: ForbiddenResponse,
    ErrorCode.NOT_FOUND: NotFoundResponse,
    ErrorCode.METHOD_NOT_ALLOWED: MethodNotAllowedResponse,
    ErrorCode.CONFLICT: ConflictResponse,
    ErrorCode.UNPROCESSABLE_ENTITY: UnprocessableEntityResponse,
    ErrorCode.TOO_MANY_REQUESTS: TooManyRequestsResponse,
    ErrorCode.INTERNAL_SERVER_ERROR: InternalServerErrorResponse,
    ErrorCode.DATABASE_ERROR: DatabaseErrorResponse,
    ErrorCode.NOT_IMPLEMENTED: NotImplementedResponse,
    ErrorCode.BAD_GATEWAY: BadGatewayResponse,
    ErrorCode.SERVICE_UNAVAILABLE: ServiceUnavailableResponse,
}


OTHER_RESPONSES: Dict[
    Union[int, str],
    Dict[
        str,
        Union[
            str,
            Type[ErrorResponse],
            List[Type[ErrorResponse]],
        ],
    ],
] = {
    400: {
        "description": "Bad Request Response",
        "model": BadRequestResponse,
    },
    401: {
        "description": "Unauthorized Response",
        "model": UnauthorizedResponse,
    },
    403: {
        "description": "Forbidden Response",
        "model": ForbiddenResponse,
    },
    404: {
        "description": "Not Found Response",
        "model": NotFoundResponse,
    },
    405: {
        "description": "Method Not Allowed Response",
        "model": MethodNotAllowedResponse,
    },
    409: {
        "description": "Conflict Response",
        "model": ConflictResponse,
    },
    422: {
        "description": "Unprocessable Entity Response",
        "model": UnprocessableEntityResponse,
    },
    429: {
        "description": "Too Many Requests Response",
        "model": TooManyRequestsResponse,
    },
    500: {
        "description": "Internal Server Error Response",
        "model": [
            InternalServerErrorResponse,
            DatabaseErrorResponse,
        ],
    },
    501: {
        "description": "Not Implemented Response",
        "model": NotImplementedResponse,
    },
    502: {
        "description": "Bad Gateway Response",
        "model": BadGatewayResponse,
    },
    503: {
        "description": "Service Unavailable Response",
        "model": ServiceUnavailableResponse,
    },
}


class SuccessResponse(
    SuccessDescriptor,
    Response[Literal[True], SuccessCode, GenericDataT, GenericPaginationT, MetadataT],
    Generic[GenericDataT, GenericPaginationT, MetadataT],
):
    success: Literal[True] = True


SuccessResponseT = TypeVar("SuccessResponseT", bound=SuccessResponse)


class AnyDataResponse(
    AnyDataSuccessDescriptor,
    SuccessResponse[DataT, GenericPaginationT, MetadataT],
    Generic[DataT, GenericPaginationT, MetadataT],
):
    pass


class NoDataResponse(
    NoDataPayload[MetadataT],
    NoDataSuccessDescriptor,
    SuccessResponse[None, None, MetadataT],
    Generic[MetadataT],
):
    data: None = None
    pagination: None = None


class SingleDataResponse(
    SingleDataPayload[DataT, MetadataT],
    SingleDataSuccessDescriptor,
    SuccessResponse[DataT, None, MetadataT],
    Generic[DataT, MetadataT],
):
    pagination: None = None


class CreateSingleDataResponse(
    CreateSingleDataPayload[DataT, MetadataT],
    CreateSingleDataSuccessDescriptor,
    SuccessResponse[DataPair[None, DataT], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class ReadSingleDataResponse(
    ReadSingleDataPayload[DataT, MetadataT],
    ReadSingleDataSuccessDescriptor,
    SuccessResponse[DataPair[DataT, None], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class UpdateSingleDataResponse(
    UpdateSingleDataPayload[DataT, MetadataT],
    UpdateSingleDataSuccessDescriptor,
    SuccessResponse[DataPair[DataT, DataT], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class DeleteSingleDataResponse(
    DeleteSingleDataPayload[DataT, MetadataT],
    DeleteSingleDataSuccessDescriptor,
    SuccessResponse[DataPair[DataT, None], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class OptionalSingleDataResponse(
    OptionalSingleDataPayload[DataT, MetadataT],
    OptionalSingleDataSuccessDescriptor,
    SuccessResponse[Optional[DataT], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pagination: None = None


class MultipleDataResponse(
    MultipleDataPayload[DataT, PaginationT, MetadataT],
    MultipleDataSuccessDescriptor,
    SuccessResponse[List[DataT], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class CreateMultipleDataResponse(
    CreateMultipleDataPayload[DataT, PaginationT, MetadataT],
    CreateMultipleDataSuccessDescriptor,
    SuccessResponse[DataPair[None, List[DataT]], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class ReadMultipleDataResponse(
    ReadMultipleDataPayload[DataT, PaginationT, MetadataT],
    ReadMultipleDataSuccessDescriptor,
    SuccessResponse[DataPair[List[DataT], None], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class UpdateMultipleDataResponse(
    UpdateMultipleDataPayload[DataT, PaginationT, MetadataT],
    UpdateMultipleDataSuccessDescriptor,
    SuccessResponse[DataPair[List[DataT], List[DataT]], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class DeleteMultipleDataResponse(
    DeleteMultipleDataPayload[DataT, PaginationT, MetadataT],
    DeleteMultipleDataSuccessDescriptor,
    SuccessResponse[DataPair[List[DataT], None], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class OptionalMultipleDataResponse(
    OptionalMultipleDataPayload[DataT, PaginationT, MetadataT],
    OptionalMultipleDataSuccessDescriptor,
    SuccessResponse[Optional[List[DataT]], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass
