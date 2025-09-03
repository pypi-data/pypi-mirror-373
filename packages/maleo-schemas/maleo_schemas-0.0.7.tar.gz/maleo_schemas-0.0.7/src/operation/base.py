import traceback
from logging import Logger
from typing import Generic, Literal
from maleo.logging.enums import Level
from maleo.mixins.general import Success, SuccessT
from maleo.mixins.operation import (
    OperationIdentifier,
    OperationSummary,
    OperationType,
)
from maleo.mixins.timestamp import OperationTimestampMixin
from maleo.types.base.boolean import OptionalBoolean
from maleo.types.base.dict import (
    OptionalStringToStringDict,
    StringToAnyDict,
    StringToStringDict,
)
from maleo.utils.merger import merge_dicts
from maleo.dtos.authentication import AuthenticationT, AuthenticationMixin
from maleo.dtos.contexts.operation import OperationContext, OperationContextMixin
from maleo.dtos.contexts.request import GenericRequestContextT, RequestContextMixin
from maleo.dtos.contexts.response import ResponseContextT, ResponseContextMixin
from maleo.dtos.contexts.service import ServiceContext, ServiceContextMixin
from maleo.dtos.error import GenericErrorT, ErrorT, ErrorMixin
from maleo.dtos.resource import ResourceT, ResourceMixin
from ..response import ResponseT, ResponseMixin
from .action import (
    OperationActionMixin,
    OperationActionT,
)


class BaseOperation(
    ResponseMixin[ResponseT],
    ResponseContextMixin[ResponseContextT],
    OperationActionMixin[OperationActionT],
    AuthenticationMixin[AuthenticationT],
    RequestContextMixin[GenericRequestContextT],
    ErrorMixin[GenericErrorT],
    Success[SuccessT],
    ResourceMixin[ResourceT],
    OperationSummary,
    OperationTimestampMixin,
    OperationContextMixin[OperationContext],
    OperationType,
    OperationIdentifier,
    ServiceContextMixin[ServiceContext],
    Generic[
        ResourceT,
        SuccessT,
        GenericErrorT,
        GenericRequestContextT,
        AuthenticationT,
        OperationActionT,
        ResponseContextT,
        ResponseT,
    ],
):
    @property
    def log_message(self) -> str:
        message = f"Operation {self.id} - {self.type} - "

        success_information = f"{'success' if self.success else 'failed'}"

        if self.response_context is not None:
            success_information += f" {self.response_context.status_code}"

        message += f"{success_information} - "

        if self.request_context is not None:
            message += (
                f"{self.request_context.method} {self.request_context.url} - "
                f"IP: {self.request_context.ip_address} - "
            )

        if self.authentication is None:
            authentication = "No Authentication"
        else:
            # * In this line, 'is_authenticated' is not detected
            # * due to the use of generic, but this property exists
            if not self.authentication.user.is_authenticated:
                authentication = "Unauthenticated"
            else:
                # * In this line, 'display_name' and 'identity' is not detected
                # * due to the use of generic, but this property exists
                authentication = (
                    "Authenticated | "
                    f"Username: {self.authentication.user.display_name} | "
                    f"Email: {self.authentication.user.identity}"
                )

        message += f"{authentication} - "
        message += self.summary

        return message

    @property
    def labels(self) -> StringToStringDict:
        labels = {
            "service": self.service_context.key,
            "environment": self.service_context.environment,
            "operation_id": str(self.id),
            "operation_type": self.type,
            "success": "true" if self.success else "false",
        }

        if self.request_context is not None:
            labels["method"] = self.request_context.method
            labels["url"] = self.request_context.url
        if self.response_context is not None:
            labels["status_code"] = str(self.response_context.status_code)

        return labels

    def log_labels(
        self,
        *,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ) -> StringToStringDict:
        if override_labels is not None:
            return override_labels

        labels = self.labels
        if additional_labels is not None:
            for k, v in additional_labels.items():
                if k in labels.keys():
                    raise ValueError(
                        f"Key '{k}' already exist in labels, override the labels if necessary"
                    )
                labels[k] = v
            labels = merge_dicts(labels, additional_labels)
        return labels

    def log_extra(
        self,
        *,
        additional_extra: OptionalStringToStringDict = None,
        override_extra: OptionalStringToStringDict = None,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ) -> StringToAnyDict:
        labels = self.log_labels(
            additional_labels=additional_labels, override_labels=override_labels
        )

        if override_extra is not None:
            extra = override_extra
        else:
            extra = {"json_fields": self.model_dump(mode="json"), "labels": labels}
            if additional_extra is not None:
                extra = merge_dicts(extra, additional_extra)

        return extra

    def log(
        self,
        logger: Logger,
        level: Level,
        *,
        exc_info: OptionalBoolean = None,
        additional_extra: OptionalStringToStringDict = None,
        override_extra: OptionalStringToStringDict = None,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ):
        try:
            message = self.log_message
            extra = self.log_extra(
                additional_extra=additional_extra,
                override_extra=override_extra,
                additional_labels=additional_labels,
                override_labels=override_labels,
            )
            logger.log(
                level,
                message,
                exc_info=exc_info,
                extra=extra,
            )
        except Exception:
            print("Failed logging operation:\n", traceback.format_exc())


class FailedBaseOperation(
    BaseOperation[
        ResourceT,
        Literal[False],
        ErrorT,
        GenericRequestContextT,
        AuthenticationT,
        OperationActionT,
        ResponseContextT,
        ResponseT,
    ],
    Generic[
        ResourceT,
        ErrorT,
        GenericRequestContextT,
        AuthenticationT,
        OperationActionT,
        ResponseContextT,
        ResponseT,
    ],
):
    success: Literal[False] = False


class SuccessfulBaseOperation(
    BaseOperation[
        ResourceT,
        Literal[True],
        None,
        GenericRequestContextT,
        AuthenticationT,
        OperationActionT,
        ResponseContextT,
        ResponseT,
    ],
    Generic[
        ResourceT,
        GenericRequestContextT,
        AuthenticationT,
        OperationActionT,
        ResponseContextT,
        ResponseT,
    ],
):
    success: Literal[True] = True
    error: None = None
