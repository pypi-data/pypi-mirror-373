import logging
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import List, Type, Union
from maleo.constants.error import ERROR_STATUS_CODE_MAP
from maleo.dtos.authentication import AuthenticationT
from maleo.dtos.error.spec import ErrorSpecT
from maleo.dtos.error import ErrorT
from maleo.enums.error import Code as ErrorCode
from maleo.logging.enums import Level, LoggerType
from maleo.schemas.response import (
    ErrorResponse,
    ErrorResponseT,
    UnauthorizedResponse,
    UnprocessableEntityResponse,
    InternalServerErrorResponse,
    ERROR_RESPONSE_MAP,
    OTHER_RESPONSES,
)
from .. import MaleoException


def authentication_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        content=UnauthorizedResponse().model_dump(mode="json"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def general_exception_handler(request: Request, exc: Exception):
    other = {
        "exc_type": type(exc).__name__,
        "exc_data": {
            "message": str(exc),
            "args": exc.args,
        },
    }

    # Get the first arg as a potential ErrorCode
    code = exc.args[0] if exc.args else None

    if isinstance(code, ErrorCode):
        error_code = code
    elif isinstance(code, str) and code in ErrorCode:
        error_code = ErrorCode[code]
    else:
        error_code = None

    if error_code:
        response_cls = ERROR_RESPONSE_MAP.get(error_code, None)
        status_code = ERROR_STATUS_CODE_MAP.get(error_code, None)

        if response_cls and status_code:
            response_obj = response_cls(other=other)  # type: ignore
            return JSONResponse(
                content=response_obj.model_dump(mode="json"),
                status_code=status_code,
            )

    return JSONResponse(
        content=InternalServerErrorResponse(other=other).model_dump(mode="json"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        content=UnprocessableEntityResponse(
            other=jsonable_encoder(exc.errors())
        ).model_dump(mode="json"),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        content=UnprocessableEntityResponse(other=exc.errors()).model_dump(mode="json"),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    other = {
        "exc_type": type(exc).__name__,
        "exc_data": {
            "status_code": exc.status_code,
            "detail": exc.detail,
            "headers": exc.headers,
        },
    }

    if exc.status_code in OTHER_RESPONSES:
        model_or_models: Union[str, Type[ErrorResponse], List[Type[ErrorResponse]]] = (
            OTHER_RESPONSES[exc.status_code]["model"]
        )

        if not isinstance(model_or_models, str):
            if isinstance(model_or_models, list):
                model_cls = model_or_models[0]
            else:
                model_cls = model_or_models

            response_obj = model_cls(other=other)  # type: ignore

            return JSONResponse(
                content=response_obj.model_dump(mode="json"),
                status_code=exc.status_code,
            )

    return JSONResponse(
        content=InternalServerErrorResponse(other=other).model_dump(mode="json"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def maleo_exception_handler(
    request: Request,
    exc: MaleoException[AuthenticationT, ErrorSpecT, ErrorT, ErrorResponseT],
):
    logger = logging.getLogger(
        f"{exc.service_context.environment} - {exc.service_context.key} - {LoggerType.EXCEPTION}"
    )

    exc.operation.log(logger, level=Level.ERROR)
    return JSONResponse(
        content=exc.response.model_dump(mode="json"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
