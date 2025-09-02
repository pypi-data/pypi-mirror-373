"""General utility functions and helper methods used across the codebase."""

import random
import string
import warnings
from datetime import datetime
from decimal import Decimal
from typing import Any, Union

import typing_extensions

from crypticorn.common.exceptions import ApiError, ExceptionContent, HTTPException
from crypticorn.common.warnings import CrypticornDeprecatedSince25


def throw_if_none(
    value: Any,
    message: str = "Object not found",
) -> None:
    """Throws an FastAPI HTTPException if the value is None. https://docs.python.org/3/library/stdtypes.html#truth-value-testing"""
    if value is None:
        raise HTTPException(
            content=ExceptionContent(error=ApiError.OBJECT_NOT_FOUND, message=message)
        )


def throw_if_falsy(
    value: Any,
    message: str = "Object not found",
) -> None:
    """Throws an FastAPI HTTPException if the value is False. https://docs.python.org/3/library/stdtypes.html#truth-value-testing"""
    if not value:
        raise HTTPException(
            content=ExceptionContent(error=ApiError.OBJECT_NOT_FOUND, message=message)
        )


def gen_random_id(length: int = 20) -> str:
    """Generate a random base62 string (a-zA-Z0-9) of specified length. The max possible combinations is 62^length.
    Kucoin max 40, bingx max 40"""
    charset = string.ascii_letters + string.digits
    return "".join(random.choice(charset) for _ in range(length))


@typing_extensions.deprecated(
    "The `is_equal` method is deprecated; use `math.is_close` instead.", category=None
)
def is_equal(
    a: Union[float, Decimal],
    b: Union[float, Decimal],
    rel_tol: float = 1e-9,
    abs_tol: float = 0.0,
) -> bool:
    """
    Compare two Decimal numbers for approximate equality.
    """
    warnings.warn(
        "The `is_equal` method is deprecated; use `math.is_close` instead.",
        category=CrypticornDeprecatedSince25,
    )
    if not isinstance(a, Decimal):
        a = Decimal(str(a))
    if not isinstance(b, Decimal):
        b = Decimal(str(b))

    # Convert tolerances to Decimal
    return Decimal(abs(a - b)) <= max(
        Decimal(str(rel_tol)) * max(abs(a), abs(b)), Decimal(str(abs_tol))
    )


def optional_import(module_name: str, extra_name: str) -> Any:
    """
    Tries to import a module. Raises `ImportError` if not found with a message to install the extra dependency.
    """
    try:
        return __import__(module_name)
    except ImportError as e:
        raise ImportError(
            f"Optional dependency '{module_name}' is required for this feature. "
            f"Install it with: pip install crypticorn[{extra_name}]"
        ) from e


def datetime_to_timestamp(v: Any):
    """Converts a datetime to a timestamp.
    Can be used as a pydantic validator.
    >>> from pydantic import BeforeValidator, BaseModel
    >>> class MyModel(BaseModel):
    ...     timestamp: Annotated[int, BeforeValidator(datetime_to_timestamp)]
    """
    if isinstance(v, list):
        return [
            int(item.timestamp()) if isinstance(item, datetime) else item for item in v
        ]
    elif isinstance(v, datetime):
        return int(v.timestamp())
    return v
