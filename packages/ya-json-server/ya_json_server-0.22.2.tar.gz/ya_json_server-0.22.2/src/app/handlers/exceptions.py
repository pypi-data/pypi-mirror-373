import logging
from enum import Enum

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.handlers.errors import (
    APIErrorDetails,
    APIException,
    APIInternalServerErrorResponse,
    APIRequestValidationErrorResponse,
    APIValidationErrorResponse,
)

logger = logging.getLogger("uvicorn")


class ResponseHeaders(Enum):
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-store",
    }
    JSON_HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        **SECURITY_HEADERS,
    }


def _details_compose(errors: list):
    return [
        APIErrorDetails(
            field=(
                "->".join([str(v) for v in error["loc"][1:]])
                if len(error["loc"]) >= 1
                else str(error["loc"][0])
            ),
            issue=(error["ctx"]["error"] if hasattr(error, "ctx") else error["msg"]),
            location=str(error["loc"][0]),
        )
        for error in errors
    ]


async def api_exception_handler(
    request: Request,
    exception: APIException | ValidationError | RequestValidationError | Exception,
):
    logger.warning(
        "api_exception_handler -> Request\
        headers: [{}] body: [{}], path_params: [{}], query_params: [{}].".format(
            request.headers,
            await request.body(),
            request.path_params,
            request.query_params,
        )
    )

    if isinstance(exception, ValidationError) or isinstance(
        exception, RequestValidationError
    ):

        details = _details_compose(exception.errors())

        if isinstance(exception, ValidationError):
            status_code = 400
            error_response = APIValidationErrorResponse(
                status_code=status_code, details=details
            )
        else:
            status_code = 422
            error_response = APIRequestValidationErrorResponse(
                status_code=status_code, details=details
            )

    elif hasattr(exception, "status_code") and hasattr(exception, "error_response"):
        status_code = exception.status_code
        error_response = exception.error_response
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_response = APIInternalServerErrorResponse(message=str(exception))

    return JSONResponse(
        content=jsonable_encoder(error_response, by_alias=True),
        headers=ResponseHeaders.JSON_HEADERS.value,
        status_code=status_code,
    )
