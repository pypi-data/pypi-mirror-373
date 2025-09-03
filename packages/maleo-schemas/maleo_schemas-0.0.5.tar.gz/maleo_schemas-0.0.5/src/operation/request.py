from typing import Generic, Literal
from maleo.enums.operation import OperationType
from maleo.mixins.general import SuccessT
from maleo.dtos.authentication import AuthenticationT, OptionalAuthentication
from maleo.dtos.error import GenericErrorT, ErrorT
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.response import ResponseContext
from ..response import ResponseT, ErrorResponseT, SuccessResponseT
from .base import BaseOperation
from .resource import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    ResourceOperationActionT,
)


class RequestOperation(
    BaseOperation[
        None,
        SuccessT,
        GenericErrorT,
        RequestContext,
        OptionalAuthentication,
        ResourceOperationActionT,
        ResponseContext,
        ResponseT,
    ],
    Generic[
        SuccessT,
        GenericErrorT,
        ResourceOperationActionT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.REQUEST
    resource: None = None


class FailedRequestOperation(
    RequestOperation[
        Literal[False],
        ErrorT,
        ResourceOperationActionT,
        ErrorResponseT,
    ],
    Generic[
        ErrorT,
        ResourceOperationActionT,
        ErrorResponseT,
    ],
):
    success: Literal[False] = False
    summary: str = "Failed processing request"


class CreateFailedRequestOperation(
    FailedRequestOperation[ErrorT, CreateResourceOperationAction, ErrorResponseT],
    Generic[ErrorT, ErrorResponseT],
):
    pass


class ReadFailedRequestOperation(
    FailedRequestOperation[ErrorT, CreateResourceOperationAction, ErrorResponseT],
    Generic[ErrorT, ErrorResponseT],
):
    pass


class UpdateFailedRequestOperation(
    FailedRequestOperation[ErrorT, UpdateResourceOperationAction, ErrorResponseT],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


class DeleteFailedRequestOperation(
    FailedRequestOperation[ErrorT, DeleteResourceOperationAction, ErrorResponseT],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


class SuccessfulRequestOperation(
    RequestOperation[
        Literal[True],
        None,
        ResourceOperationActionT,
        SuccessResponseT,
    ],
    Generic[
        ResourceOperationActionT,
        SuccessResponseT,
    ],
):
    success: Literal[True] = True
    error: None = None
    summary: str = "Successfully processed request"


class CreateSuccessfulRequestOperation(
    SuccessfulRequestOperation[CreateResourceOperationAction, SuccessResponseT],
    Generic[AuthenticationT, SuccessResponseT],
):
    pass


class ReadSuccessfulRequestOperation(
    SuccessfulRequestOperation[ReadResourceOperationAction, SuccessResponseT],
    Generic[AuthenticationT, SuccessResponseT],
):
    pass


class UpdateSuccessfulRequestOperation(
    SuccessfulRequestOperation[UpdateResourceOperationAction, SuccessResponseT],
    Generic[AuthenticationT, SuccessResponseT],
):
    pass


class DeleteSuccessfulRequestOperation(
    SuccessfulRequestOperation[DeleteResourceOperationAction, SuccessResponseT],
    Generic[AuthenticationT, SuccessResponseT],
):
    pass
