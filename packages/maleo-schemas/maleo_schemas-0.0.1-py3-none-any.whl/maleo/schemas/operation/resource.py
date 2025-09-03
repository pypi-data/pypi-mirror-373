import re
from fastapi import Request
from pydantic import BaseModel, Field
from typing import Generic, Literal, Optional, TypeVar, Union, overload
from uuid import UUID
from maleo.enums.operation import (
    OperationType,
    ResourceOperationType,
    ResourceOperationCreateType,
    ResourceOperationUpdateType,
    ResourceOperationDataUpdateType,
    ResourceOperationStatusUpdateType,
)
from maleo.mixins.general import SuccessT
from maleo.mixins.timestamp import OperationTimestamp
from maleo.dtos.authentication import AuthenticationT
from maleo.dtos.data import DataT
from maleo.dtos.contexts.operation import OperationContext
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.error import GenericErrorT, ErrorT
from maleo.dtos.metadata import MetadataT
from maleo.dtos.pagination import PaginationT
from maleo.dtos.resource import Resource
from ..response import (
    ResponseT,
    ErrorResponseT,
    SuccessResponseT,
    NoDataResponse,
    CreateSingleDataResponse,
    ReadSingleDataResponse,
    UpdateSingleDataResponse,
    DeleteSingleDataResponse,
    CreateMultipleDataResponse,
    ReadMultipleDataResponse,
    UpdateMultipleDataResponse,
    DeleteMultipleDataResponse,
)
from .base import BaseOperation


class ResourceOperationAction(BaseModel):
    type: ResourceOperationType = Field(..., description="Resource operation's type")
    create_type: Optional[ResourceOperationCreateType] = Field(
        None, description="Resource operation's create type (optional)"
    )
    update_type: Optional[ResourceOperationUpdateType] = Field(
        None, description="Resource operation's update type (optional)"
    )
    data_update_type: Optional[ResourceOperationDataUpdateType] = Field(
        None, description="Resource operation's data update type (optional)"
    )
    status_update_type: Optional[ResourceOperationStatusUpdateType] = Field(
        None, description="Resource operation's status update type (optional)"
    )


class CreateResourceOperationAction(ResourceOperationAction):
    type: ResourceOperationType = ResourceOperationType.CREATE
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


class ReadResourceOperationAction(ResourceOperationAction):
    type: ResourceOperationType = ResourceOperationType.READ
    create_type: Optional[ResourceOperationCreateType] = None
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


class UpdateResourceOperationAction(ResourceOperationAction):
    type: ResourceOperationType = ResourceOperationType.UPDATE
    create_type: Optional[ResourceOperationCreateType] = None


class DeleteResourceOperationAction(ResourceOperationAction):
    type: ResourceOperationType = ResourceOperationType.DELETE
    create_type: Optional[ResourceOperationCreateType] = None
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


AllResourceOperationAction = Union[
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
]


def extract_resource_operation_action(
    request: Request, from_state: bool = True
) -> AllResourceOperationAction:
    if from_state:
        operation_action = request.state.resource_operation_action

        if not isinstance(
            operation_action,
            (
                CreateResourceOperationAction,
                ReadResourceOperationAction,
                UpdateResourceOperationAction,
                DeleteResourceOperationAction,
            ),
        ):
            raise TypeError(
                f"Invalid type of 'resource_operation_action': '{type(operation_action)}'"
            )

        return operation_action

    else:
        create_type = None
        update_type = None
        data_update_type = None
        status_update_type = None

        if request.method == "POST":
            if request.url.path.endswith("/restore"):
                create_type = ResourceOperationCreateType.RESTORE
            else:
                create_type = ResourceOperationCreateType.NEW
            return CreateResourceOperationAction(create_type=create_type)
        elif request.method == "GET":
            return ReadResourceOperationAction()
        elif request.method in ["PATCH", "PUT"]:
            if request.method == "PUT":
                update_type = ResourceOperationUpdateType.DATA
                data_update_type = ResourceOperationDataUpdateType.FULL
            elif request.method == "PATCH":
                if request.url.path.endswith("/status"):
                    update_type = ResourceOperationUpdateType.STATUS
                    if request.query_params is not None:
                        match = re.search(
                            r"[?&]action=([^&]+)",
                            (
                                ""
                                if not request.query_params
                                else str(request.query_params)
                            ),
                        )
                        if match:
                            try:
                                status_update_type = ResourceOperationStatusUpdateType(
                                    match.group(1)
                                )
                            except Exception:
                                pass
                else:
                    update_type = ResourceOperationUpdateType.DATA
                    data_update_type = ResourceOperationDataUpdateType.PARTIAL
            return UpdateResourceOperationAction(
                update_type=update_type,
                data_update_type=data_update_type,
                status_update_type=status_update_type,
            )
        elif request.method == "DELETE":
            return DeleteResourceOperationAction()
        else:
            raise ValueError("Unable to determine resource operation action")


def resource_operation_action_dependency(from_state: bool = True):

    def dependency(request: Request) -> AllResourceOperationAction:
        return extract_resource_operation_action(request, from_state=from_state)

    return dependency


ResourceOperationActionT = TypeVar(
    "ResourceOperationActionT", bound=ResourceOperationAction
)


class ResourceOperationActionMixin(BaseModel, Generic[ResourceOperationActionT]):
    action: ResourceOperationActionT = Field(..., description="Operation's action.")


@overload
def generate_resource_operation_action(
    *,
    type: Literal[ResourceOperationType.CREATE],
    create_type: Optional[ResourceOperationCreateType] = ...,
) -> CreateResourceOperationAction: ...
@overload
def generate_resource_operation_action(
    *,
    type: Literal[ResourceOperationType.READ],
) -> ReadResourceOperationAction: ...
@overload
def generate_resource_operation_action(
    *,
    type: Literal[ResourceOperationType.UPDATE],
    update_type: Optional[ResourceOperationUpdateType] = ...,
    data_update_type: Optional[ResourceOperationDataUpdateType] = ...,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = ...,
) -> UpdateResourceOperationAction: ...
@overload
def generate_resource_operation_action(
    *,
    type: Literal[ResourceOperationType.DELETE],
) -> DeleteResourceOperationAction: ...
def generate_resource_operation_action(
    *,
    type: ResourceOperationType,
    create_type: Optional[ResourceOperationCreateType] = None,
    update_type: Optional[ResourceOperationUpdateType] = None,
    data_update_type: Optional[ResourceOperationDataUpdateType] = None,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None,
) -> AllResourceOperationAction:
    if not isinstance(type, ResourceOperationType):
        raise ValueError(f"Unsupported `type`: {type}")

    if type is ResourceOperationType.CREATE:
        return CreateResourceOperationAction(create_type=create_type)

    elif type is ResourceOperationType.READ:
        return ReadResourceOperationAction()

    elif type is ResourceOperationType.UPDATE:
        return UpdateResourceOperationAction(
            update_type=update_type,
            data_update_type=data_update_type,
            status_update_type=status_update_type,
        )

    elif type is ResourceOperationType.DELETE:
        return DeleteResourceOperationAction()


def resource_operation_action_from_request(
    request: Request, from_state: bool = True
) -> AllResourceOperationAction:
    if from_state:
        operation_action = request.state.operation_action

        if operation_action is None:
            raise ValueError(
                "Can not retrieve 'operation_action' from the current request state"
            )

        if not isinstance(
            operation_action,
            (
                CreateResourceOperationAction,
                ReadResourceOperationAction,
                UpdateResourceOperationAction,
                DeleteResourceOperationAction,
            ),
        ):
            raise ValueError(
                f"Invalid 'operation_action' type: '{type(operation_action)}'"
            )

        return operation_action

    if request.method == "POST":
        if request.url.path.endswith("/restore"):
            return generate_resource_operation_action(
                type=ResourceOperationType.CREATE,
                create_type=ResourceOperationCreateType.RESTORE,
            )
        else:
            return generate_resource_operation_action(
                type=ResourceOperationType.CREATE,
                create_type=ResourceOperationCreateType.NEW,
            )

    elif request.method == "GET":
        return generate_resource_operation_action(
            type=ResourceOperationType.READ,
        )

    elif request.method in ["PATCH", "PUT"]:
        if request.method == "PUT":
            return generate_resource_operation_action(
                type=ResourceOperationType.UPDATE,
                update_type=ResourceOperationUpdateType.DATA,
            )
        elif request.method == "PATCH":
            if not request.url.path.endswith("/status"):
                return generate_resource_operation_action(
                    type=ResourceOperationType.UPDATE,
                    update_type=ResourceOperationUpdateType.DATA,
                )
            else:
                if request.query_params is not None:
                    match = re.search(
                        r"[?&]action=([^&]+)",
                        ("" if not request.query_params else str(request.query_params)),
                    )
                    if match:
                        try:
                            return generate_resource_operation_action(
                                type=ResourceOperationType.UPDATE,
                                update_type=ResourceOperationUpdateType.STATUS,
                                status_update_type=ResourceOperationStatusUpdateType(
                                    match.group(1)
                                ),
                            )
                        except Exception:
                            return generate_resource_operation_action(
                                type=ResourceOperationType.UPDATE,
                                update_type=ResourceOperationUpdateType.STATUS,
                                status_update_type=None,
                            )

    elif request.method == "DELETE":
        return generate_resource_operation_action(
            type=ResourceOperationType.DELETE,
        )

    raise ValueError("Unable to map request's 'method' to 'operation_type'")


class ResourceOperation(
    BaseOperation[
        Resource,
        SuccessT,
        GenericErrorT,
        Optional[RequestContext],
        AuthenticationT,
        ResourceOperationActionT,
        None,
        ResponseT,
    ],
    Generic[
        SuccessT,
        GenericErrorT,
        AuthenticationT,
        ResourceOperationActionT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.RESOURCE
    response_context: None = None


class FailedResourceOperation(
    ResourceOperation[
        Literal[False],
        ErrorT,
        AuthenticationT,
        ResourceOperationActionT,
        ErrorResponseT,
    ],
    Generic[ErrorT, AuthenticationT, ResourceOperationActionT, ErrorResponseT],
):
    success: Literal[False] = False


class CreateFailedResourceOperation(
    FailedResourceOperation[
        ErrorT,
        AuthenticationT,
        CreateResourceOperationAction,
        ErrorResponseT,
    ],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


class ReadFailedResourceOperation(
    FailedResourceOperation[
        ErrorT, AuthenticationT, ReadResourceOperationAction, ErrorResponseT
    ],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


class UpdateFailedResourceOperation(
    FailedResourceOperation[
        ErrorT,
        AuthenticationT,
        UpdateResourceOperationAction,
        ErrorResponseT,
    ],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


class DeleteFailedResourceOperation(
    FailedResourceOperation[
        ErrorT,
        AuthenticationT,
        DeleteResourceOperationAction,
        ErrorResponseT,
    ],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    pass


@overload
def generate_failed_resource_operation(
    action: CreateResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> CreateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_resource_operation(
    action: ReadResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> ReadFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_resource_operation(
    action: UpdateResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> UpdateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_resource_operation(
    action: DeleteResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> DeleteFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_resource_operation(
    *,
    type: Literal[ResourceOperationType.CREATE],
    create_type: Optional[ResourceOperationCreateType] = ...,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> CreateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_resource_operation(
    *,
    type: Literal[ResourceOperationType.READ],
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> ReadFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_resource_operation(
    *,
    type: Literal[ResourceOperationType.UPDATE],
    update_type: Optional[ResourceOperationUpdateType] = ...,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = ...,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> UpdateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
@overload
def generate_failed_resource_operation(
    *,
    type: Literal[ResourceOperationType.DELETE],
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> DeleteFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT]: ...
def generate_failed_resource_operation(
    action: Optional[AllResourceOperationAction] = None,
    *,
    type: Optional[ResourceOperationType] = None,
    create_type: Optional[ResourceOperationCreateType] = None,
    update_type: Optional[ResourceOperationUpdateType] = None,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContext,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorT,
    request_context: Optional[RequestContext],
    authentication: AuthenticationT,
    resource: Resource,
    response: ErrorResponseT,
) -> Union[
    CreateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
    ReadFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
    UpdateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
    DeleteFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
]:
    if (action is None and type is None) or (action is not None and type is not None):
        raise ValueError("Only either 'action' or 'type' must be given")

    if action is not None:
        if not isinstance(
            action,
            (
                CreateResourceOperationAction,
                ReadResourceOperationAction,
                UpdateResourceOperationAction,
                DeleteResourceOperationAction,
            ),
        ):
            raise ValueError(f"Invalid 'action' type: '{type(action)}'")

        if isinstance(action, CreateResourceOperationAction):
            return CreateFailedResourceOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                resource=resource,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response=response,
            )
        elif isinstance(action, ReadResourceOperationAction):
            return ReadFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                resource=resource,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response=response,
            )
        elif isinstance(action, UpdateResourceOperationAction):
            return UpdateFailedResourceOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                resource=resource,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response=response,
            )
        elif isinstance(action, DeleteResourceOperationAction):
            return DeleteFailedResourceOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                resource=resource,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response=response,
            )

    elif type is not None:
        if not isinstance(type, ResourceOperationType):
            raise ValueError(f"Unsupported `type`: {type}")

        if type is ResourceOperationType.CREATE:
            action = generate_resource_operation_action(
                type=type, create_type=create_type
            )
            return CreateFailedResourceOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                resource=resource,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response=response,
            )
        elif type is ResourceOperationType.READ:
            action = generate_resource_operation_action(type=type)
            return ReadFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                resource=resource,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response=response,
            )
        elif type is ResourceOperationType.UPDATE:
            action = generate_resource_operation_action(
                type=type,
                update_type=update_type,
                status_update_type=status_update_type,
            )
            return UpdateFailedResourceOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                resource=resource,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response=response,
            )
        elif type is ResourceOperationType.DELETE:
            action = generate_resource_operation_action(type=type)
            return DeleteFailedResourceOperation[
                ErrorT, AuthenticationT, ErrorResponseT
            ](
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                resource=resource,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                response=response,
            )
    else:
        # This should never happen due to initial validation,
        # but type checker needs to see all paths covered
        raise ValueError("Neither 'action' nor 'type' provided")


class SuccessfulResourceOperation(
    ResourceOperation[
        Literal[True],
        None,
        AuthenticationT,
        ResourceOperationActionT,
        SuccessResponseT,
    ],
    Generic[AuthenticationT, ResourceOperationActionT, SuccessResponseT],
):
    success: Literal[True] = True
    error: None = None


class NoDataResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        ResourceOperationActionT,
        NoDataResponse[MetadataT],
    ],
    Generic[ResourceOperationActionT, AuthenticationT, MetadataT],
):
    pass


class CreateSingleResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        CreateResourceOperationAction,
        CreateSingleDataResponse[DataT, MetadataT],
    ],
    Generic[
        AuthenticationT,
        DataT,
        MetadataT,
    ],
):
    pass


class ReadSingleResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        ReadResourceOperationAction,
        ReadSingleDataResponse[DataT, MetadataT],
    ],
    Generic[
        AuthenticationT,
        DataT,
        MetadataT,
    ],
):
    pass


class UpdateSingleResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        UpdateResourceOperationAction,
        UpdateSingleDataResponse[DataT, MetadataT],
    ],
    Generic[
        AuthenticationT,
        DataT,
        MetadataT,
    ],
):
    pass


class DeleteSingleResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        DeleteResourceOperationAction,
        DeleteSingleDataResponse[DataT, MetadataT],
    ],
    Generic[
        AuthenticationT,
        DataT,
        MetadataT,
    ],
):
    pass


class CreateMultipleResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        CreateResourceOperationAction,
        CreateMultipleDataResponse[DataT, PaginationT, MetadataT],
    ],
    Generic[
        AuthenticationT,
        DataT,
        PaginationT,
        MetadataT,
    ],
):
    pass


class ReadMultipleResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        ReadResourceOperationAction,
        ReadMultipleDataResponse[DataT, PaginationT, MetadataT],
    ],
    Generic[
        AuthenticationT,
        DataT,
        PaginationT,
        MetadataT,
    ],
):
    pass


class UpdateMultipleResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        UpdateResourceOperationAction,
        UpdateMultipleDataResponse[DataT, PaginationT, MetadataT],
    ],
    Generic[
        AuthenticationT,
        DataT,
        PaginationT,
        MetadataT,
    ],
):
    pass


class DeleteMultipleResourceOperation(
    SuccessfulResourceOperation[
        AuthenticationT,
        DeleteResourceOperationAction,
        DeleteMultipleDataResponse[DataT, PaginationT, MetadataT],
    ],
    Generic[
        AuthenticationT,
        DataT,
        PaginationT,
        MetadataT,
    ],
):
    pass
