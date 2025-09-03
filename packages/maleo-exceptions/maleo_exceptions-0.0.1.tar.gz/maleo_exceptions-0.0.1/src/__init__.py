import traceback as tb
from typing import Generic, Literal, Optional, Type, Union, overload
from uuid import uuid4
from maleo.enums.error import Code as ErrorCode, ErrorType
from maleo.enums.operation import OperationType
from maleo.mixins.timestamp import OperationTimestamp
from maleo.types.base.any import OptionalAny
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import ListOfStrings, OptionalString
from maleo.types.base.uuid import OptionalUUID
from maleo.dtos.authentication import AuthenticationT
from maleo.dtos.contexts.operation import OperationContext
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.error import ErrorT
from maleo.dtos.error.metadata import ErrorMetadata
from maleo.dtos.error.spec import ErrorSpecT
from maleo.schemas.operation.resource import (
    AllResourceOperationAction,
    CreateFailedResourceOperation,
    ReadFailedResourceOperation,
    UpdateFailedResourceOperation,
    DeleteFailedResourceOperation,
    generate_failed_resource_operation,
)
from maleo.schemas.operation.system import SystemOperationAction, FailedSystemOperation
from maleo.dtos.resource import Resource
from maleo.schemas.response import ErrorResponseT


class MaleoException(
    Exception,
    Generic[
        AuthenticationT,
        ErrorSpecT,
        ErrorT,
        ErrorResponseT,
    ],
):
    error_spec_cls: Type[ErrorSpecT]
    error_cls: Type[ErrorT]
    response_cls: Type[ErrorResponseT]

    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.REQUEST],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "Request operation failed due to exception being raised",
        operation_action: AllResourceOperationAction,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        details: OptionalAny = None,
        response: ErrorResponseT,
    ) -> None: ...
    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.REQUEST],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "Request operation failed due to exception being raised",
        operation_action: AllResourceOperationAction,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        details: OptionalAny = None,
        error_type: ErrorType,
        status_code: int,
        error_code: ErrorCode,
        response_message: str,
        response_description: str,
    ) -> None: ...
    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.RESOURCE],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "Resource operation failed due to exception being raised",
        operation_action: AllResourceOperationAction,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        resource: Optional[Resource] = None,
        details: OptionalAny = None,
        response: ErrorResponseT,
    ) -> None: ...
    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.RESOURCE],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "Resource operation failed due to exception being raised",
        operation_action: AllResourceOperationAction,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        resource: Optional[Resource] = None,
        details: OptionalAny = None,
        error_type: ErrorType,
        status_code: int,
        error_code: ErrorCode,
        response_message: str,
        response_description: str,
    ) -> None: ...
    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.SYSTEM],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "System operation failed due to exception being raised",
        operation_action: SystemOperationAction,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        resource: Optional[Resource] = None,
        details: OptionalAny = None,
        response: ErrorResponseT,
    ) -> None: ...
    @overload
    def __init__(
        self,
        operation_type: Literal[OperationType.SYSTEM],
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "System operation failed due to exception being raised",
        operation_action: SystemOperationAction,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        resource: Optional[Resource] = None,
        details: OptionalAny = None,
        error_type: ErrorType,
        status_code: int,
        error_code: ErrorCode,
        response_message: str,
        response_description: str,
    ) -> None: ...
    def __init__(
        self,
        operation_type: OperationType,
        *args: object,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: OperationContext,
        operation_timestamp: Optional[OperationTimestamp] = None,
        operation_summary: str = "Operation failed due to exception being raised",
        operation_action: Union[SystemOperationAction, AllResourceOperationAction],
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        resource: Optional[Resource] = None,
        details: OptionalAny = None,
        response: Optional[ErrorResponseT] = None,
        error_type: Optional[ErrorType] = None,
        status_code: OptionalInteger = None,
        error_code: Optional[ErrorCode] = None,
        response_message: OptionalString = None,
        response_description: OptionalString = None,
    ) -> None:
        super().__init__(*args)

        self.service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        self.operation_id = operation_id if operation_id is not None else uuid4()
        self.operation_context = operation_context

        self.operation_timestamp = (
            operation_timestamp
            if operation_timestamp is not None
            else OperationTimestamp.now()
        )

        self.operation_summary = operation_summary
        self.request_context = request_context
        self.authentication = authentication
        self.operation_action = operation_action
        self.resource = resource
        self.details = details

        if response is None:
            if error_type is None:
                raise ValueError(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Failed generating exception, 'error_type' is not given",
                )
            self.error_type = error_type
            if status_code is None:
                raise ValueError(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Failed generating exception, 'status_code' is not given",
                )
            self.status_code = status_code
            if error_code is None:
                raise ValueError(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Failed generating exception, 'error_code' is not given",
                )
            self.error_code = error_code
            if response_message is None:
                raise ValueError(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Failed generating exception, 'response_message' is not given",
                )
            self.response_message = response_message
            if response_description is None:
                raise ValueError(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Failed generating exception, 'response_description' is not given",
                )
            self.response_description = response_description
            self.response = self.response_cls(
                code=error_code,
                message=response_message,
                description=response_description,
            )

    @property
    def error_spec(self) -> ErrorSpecT:
        return self.error_spec_cls(
            type=self.error_type,
            status_code=self.status_code,
            code=self.error_code,
            message=self.response_message,
            description=self.response_description,
        )

    @property
    def traceback(self) -> ListOfStrings:
        return tb.format_exception(self)

    @property
    def error_metadata(self) -> ErrorMetadata:
        return ErrorMetadata(details=self.details, traceback=self.traceback)

    @property
    def error(self) -> ErrorT:
        return self.error_cls.model_validate(
            {**self.error_spec.model_dump(), **self.error_metadata.model_dump()}
        )

    @property
    def operation(
        self,
    ) -> Union[
        CreateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        ReadFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        UpdateFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        DeleteFailedResourceOperation[ErrorT, AuthenticationT, ErrorResponseT],
        FailedSystemOperation[ErrorT, AuthenticationT, ErrorResponseT],
    ]:
        if isinstance(self.operation_action, SystemOperationAction):
            return FailedSystemOperation[ErrorT, AuthenticationT, ErrorResponseT](
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary="Failed system operation",
                error=self.error,
                request_context=self.request_context,
                authentication=self.authentication,
                action=self.operation_action,
                response=self.response,
            )
        else:
            if self.resource is None:
                raise ValueError(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Resource must be given for resource operation exception",
                )
            return generate_failed_resource_operation(
                action=self.operation_action,
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary=self.operation_summary,
                error=self.error,
                request_context=self.request_context,
                authentication=self.authentication,
                resource=self.resource,
                response=self.response,
            )
