import logging
from enum import Enum
from uuid import uuid4

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("uvicorn")


class APIMessageError(str, Enum):
    UNEXPECTED_ERROR = "Unexpected error."
    VALIDATION_ERROR = "Incorrectly reported attributes."
    REQUEST_ERROR = "Invalid request content."
    NOT_FOUND = "Data not found."
    UNAUTHORIZED_ERROR = "Unauthorized access."
    FORBIDDEN_ERROR = "Forbidden access."
    CONFLICT = "Conflicting data."
    PRECONDITION_FAILED = "Failed to validate conditions."


class APIErrorDetails(BaseModel):
    field: str
    issue: str
    location: str


class APIErrorResponse(BaseModel):
    namespace: str = Field(default=__name__)
    information_link: str = Field(default="http://api.localhost:<port>/docs")
    code: str
    name: str
    message: str | None = None
    correlation_id: str | None = Field(default=None, alias="correlationId")
    debug_id: str | None = Field(default=str(uuid4()), alias="debugId")
    details: list[APIErrorDetails] | None = []


class APIInternalServerErrorResponse(APIErrorResponse):
    name: str = "INTERNAL_SERVER_ERROR"
    code: str = "IE001"
    message: str = APIMessageError.UNEXPECTED_ERROR


class APIServiceUnavailableErrorResponse(APIErrorResponse):
    name: str = "SERVICE_UNAVAILABLE_ERROR"
    code: str = "IE002"
    message: str = APIMessageError.UNEXPECTED_ERROR


class APIValidationErrorResponse(APIErrorResponse):
    name: str = "VALIDATION_ERROR"
    code: str = "VE001"
    message: str = APIMessageError.VALIDATION_ERROR
    details: list[APIErrorDetails] | None = None


class APIRequestValidationErrorResponse(APIErrorResponse):
    name: str = "VALIDATION_ERROR"
    code: str = "VE002"
    message: str = APIMessageError.REQUEST_ERROR


class APIValidationUnauthorizedResponse(APIErrorResponse):
    name: str = "VALIDATION_ERROR"
    code: str = "VE003"
    message: str = APIMessageError.UNAUTHORIZED_ERROR
    details: list[APIErrorDetails] | None = None


class APIValidationForbiddenResponse(APIErrorResponse):
    name: str = "VALIDATION_ERROR"
    code: str = "VE004"
    message: str = APIMessageError.FORBIDDEN_ERROR
    details: list[APIErrorDetails] | None = None


class APIDataNotFoundResponse(APIErrorResponse):
    name: str = "NOT_FOUND"
    code: str = "NF001"
    message: str = APIMessageError.NOT_FOUND


class APIDataConflitResponse(APIErrorResponse):
    name: str = "VALIDATION_ERROR"
    code: str = "VE005"
    message: str = APIMessageError.CONFLICT


class APIDataPreconditionFailedResponse(APIErrorResponse):
    name: str = "VALIDATION_ERROR"
    code: str = "VE006"
    message: str = APIMessageError.PRECONDITION_FAILED


API_ERRORS_RESPONSES_MAP = {
    status.HTTP_400_BAD_REQUEST: APIRequestValidationErrorResponse,
    status.HTTP_404_NOT_FOUND: APIDataNotFoundResponse,
    status.HTTP_422_UNPROCESSABLE_ENTITY: APIValidationErrorResponse,
    status.HTTP_500_INTERNAL_SERVER_ERROR: APIInternalServerErrorResponse,
    status.HTTP_503_SERVICE_UNAVAILABLE: APIServiceUnavailableErrorResponse,
    status.HTTP_401_UNAUTHORIZED: APIValidationUnauthorizedResponse,
    status.HTTP_403_FORBIDDEN: APIValidationForbiddenResponse,
    status.HTTP_409_CONFLICT: APIDataConflitResponse,
    status.HTTP_412_PRECONDITION_FAILED: APIDataPreconditionFailedResponse,
}


class APIException(Exception):

    def __init__(
        self,
        status_code: int,
        message: str | None = None,
        code: str | None = None,
        details: RequestValidationError | ValidationError | None = None,
    ):
        self.status_code = status_code
        self.api_error = API_ERRORS_RESPONSES_MAP.get(
            status_code, APIMessageError.UNEXPECTED_ERROR
        )

        self.error_response: APIErrorResponse = self.api_error()
        if message:
            self.error_response.message = message
        if code:
            self.error_response.code = code
        if isinstance(details, RequestValidationError) or isinstance(
            details, ValidationError
        ):
            self.error_response.details = details


class APIExceptionError(APIException): ...


class APIExceptionWarning(APIException): ...


class APIExceptionInfo(APIException): ...


class ResponseHeaders(Enum):
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-store",
    }
    JSON_HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        **SECURITY_HEADERS,
    }


async def api_exception_handler(
    request: Request,
    exception: APIException | ValidationError | RequestValidationError | Exception,
):
    if isinstance(exception, ValidationError) or isinstance(
        exception, RequestValidationError
    ):
        errors = exception.errors()

        details = [
            APIErrorDetails(
                field=(
                    "->".join([str(v) for v in error["loc"][1:]])
                    if len(error["loc"]) >= 1
                    else str(error["loc"][0])
                ),
                issue=(
                    error["ctx"]["error"] if hasattr(error, "ctx") else error["msg"]
                ),
                location=str(error["loc"][0]),
            )
            for error in errors
        ]

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
