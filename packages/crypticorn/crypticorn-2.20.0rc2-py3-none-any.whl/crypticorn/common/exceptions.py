import json
import logging
from typing import Any, Optional

from fastapi import FastAPI
from fastapi import HTTPException as FastAPIHTTPException
from fastapi import Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from crypticorn.common.errors import (
    ApiError,
    ApiErrorIdentifier,
    ApiErrorLevel,
    ApiErrorType,
)

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum

_logger = logging.getLogger("crypticorn")


class _ExceptionType(StrEnum):
    """The protocol the exception is called from"""

    HTTP = "http"
    WEBSOCKET = "websocket"


class ExceptionDetail(BaseModel):
    """Exception details returned to the client."""

    message: Optional[str] = Field(None, description="An additional error message")
    code: ApiErrorIdentifier = Field(..., description="The unique error code")
    type: ApiErrorType = Field(..., description="The type of error")
    level: ApiErrorLevel = Field(..., description="The level of the error")
    status_code: int = Field(..., description="The HTTP status code")
    details: Any = Field(None, description="Additional details about the error")


class ExceptionContent(BaseModel):
    """Exception content used when raising an exception."""

    error: ApiError = Field(..., description="The unique error code")
    message: Optional[str] = Field(None, description="An additional error message")
    details: Any = Field(None, description="Additional details about the error")

    def enrich(
        self, _type: Optional[_ExceptionType] = _ExceptionType.HTTP
    ) -> ExceptionDetail:
        return ExceptionDetail(
            message=self.message,
            code=self.error.identifier,
            type=self.error.type,
            level=self.error.level,
            status_code=(
                self.error.http_code
                if _type == _ExceptionType.HTTP
                else self.error.websocket_code
            ),
            details=self.details,
        )


class HTTPException(FastAPIHTTPException):
    """A custom HTTP exception wrapper around FastAPI's HTTPException.
    It allows for a more structured way to handle errors, with a message and an error code. The status code is being derived from the detail's error.
        The ApiError class is the source of truth. If the error is not yet implemented, there are fallbacks in place.
    """

    def __init__(
        self,
        content: ExceptionContent,
        headers: Optional[dict[str, str]] = None,
        _type: Optional[_ExceptionType] = _ExceptionType.HTTP,
    ):
        self.content = content
        self.headers = headers
        assert isinstance(content, ExceptionContent)
        body = content.enrich(_type)
        super().__init__(
            status_code=body.status_code,
            detail=body.model_dump(mode="json"),
            headers=headers,
        )


class WebSocketException(HTTPException):
    """A WebSocketException is to be used for WebSocket connections. It is a wrapper around the HTTPException class to maintain the same structure, but using a different status code.
    To be used in the same way as the HTTPException.
    """

    def __init__(
        self, content: ExceptionContent, headers: Optional[dict[str, str]] = None
    ):
        super().__init__(content, headers, _type=_ExceptionType.WEBSOCKET)

    @classmethod
    def from_http_exception(cls, http_exception: HTTPException):
        """Helper method to convert an HTTPException to a WebSocketException."""
        return WebSocketException(
            content=http_exception.content,
            headers=http_exception.headers,
        )


async def general_handler(request: Request, exc: Exception) -> JSONResponse:
    """Default exception handler for all exceptions."""
    body = ExceptionContent(message=str(exc), error=ApiError.UNKNOWN_ERROR)
    http_exc = HTTPException(content=body)
    res = JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
        headers=http_exc.headers,
    )
    _logger.error(f"General error: {json.loads(res.__dict__.get('body'))}")
    return res


async def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Exception handler for all request validation errors."""
    body = ExceptionContent(message=str(exc), error=ApiError.INVALID_DATA_REQUEST)
    http_exc = HTTPException(content=body)
    res = JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
        headers=http_exc.headers,
    )
    _logger.error(f"Request validation error: {json.loads(res.__dict__.get('body'))}")
    return res


async def response_validation_handler(
    request: Request, exc: ResponseValidationError
) -> JSONResponse:
    """Exception handler for all response validation errors."""
    body = ExceptionContent(message=str(exc), error=ApiError.INVALID_DATA_RESPONSE)
    http_exc = HTTPException(content=body)
    res = JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
        headers=http_exc.headers,
    )
    _logger.error(f"Response validation error: {json.loads(res.__dict__.get('body'))}")
    return res


async def http_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Exception handler for HTTPExceptions. It unwraps the HTTPException and returns the detail in a flat JSON response."""
    res = JSONResponse(
        status_code=exc.status_code, content=exc.detail, headers=exc.headers
    )
    _logger.error(f"HTTP error: {json.loads(res.__dict__.get('body'))}")
    return res


def register_exception_handlers(app: FastAPI):
    """Utility to register serveral exception handlers in one go. Catches Exception, HTTPException and Data Validation errors, logs them and responds with a unified json body."""
    app.add_exception_handler(Exception, general_handler)
    app.add_exception_handler(FastAPIHTTPException, http_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(ResponseValidationError, response_validation_handler)


exception_response = {
    "default": {"model": ExceptionDetail, "description": "Error response"}
}


class CrypticornException(Exception):
    """A custom exception class for Crypticorn."""

    def __init__(self, error: ApiError, message: str = None):
        self.message = message
        self.error = error

    def __str__(self):
        return f"{self.error.identifier}: {self.message}"
