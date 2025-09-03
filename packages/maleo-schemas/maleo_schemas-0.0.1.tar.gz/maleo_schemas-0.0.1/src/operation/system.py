from pydantic import BaseModel, Field
from typing import Generic, Literal, Optional, TypeVar
from maleo.mixins.general import SuccessT
from maleo.enums.operation import OperationType, SystemOperationType
from maleo.types.base.dict import OptionalStringToAnyDict
from maleo.dtos.authentication import AuthenticationT
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.error import (
    GenericErrorT,
    ErrorT,
)
from ..response import ResponseT, ErrorResponseT, SuccessResponseT
from .base import BaseOperation


class SystemOperationAction(BaseModel):
    type: SystemOperationType = Field(..., description="Action's type")
    details: OptionalStringToAnyDict = Field(None, description="Action's details")


SystemOperationActionT = TypeVar(
    "SystemOperationActionT", bound=Optional[SystemOperationAction]
)


class SystemOperationActionMixin(BaseModel, Generic[SystemOperationActionT]):
    action: SystemOperationActionT = Field(..., description="Operation's action")


class SystemOperation(
    BaseOperation[
        None,
        SuccessT,
        GenericErrorT,
        Optional[RequestContext],
        AuthenticationT,
        SystemOperationAction,
        None,
        ResponseT,
    ],
    Generic[
        SuccessT,
        GenericErrorT,
        AuthenticationT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.SYSTEM
    resource: None = None
    response_context: None = None


class FailedSystemOperation(
    SystemOperation[Literal[False], ErrorT, AuthenticationT, ErrorResponseT],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    success: Literal[False] = False


class SuccessfulSystemOperation(
    SystemOperation[Literal[True], None, AuthenticationT, SuccessResponseT],
    Generic[AuthenticationT, SuccessResponseT],
):
    success: Literal[True] = True
    error: None = None
