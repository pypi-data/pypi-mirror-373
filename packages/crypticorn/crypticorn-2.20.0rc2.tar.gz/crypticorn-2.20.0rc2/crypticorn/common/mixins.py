import logging
import warnings
from enum import EnumMeta

from crypticorn.common.warnings import CrypticornDeprecatedSince28

_logger = logging.getLogger("crypticorn")


class ValidateEnumMixin:
    """
    Mixin for validating enum values manually.

    ⚠️ Note:
    This does NOT enforce validation automatically on enum creation.
    It's up to the developer to call `Class.validate(value)` where needed.

    Usage:
        >>> class Color(ValidateEnumMixin, StrEnum):
        >>>     RED = "red"
        >>>     GREEN = "green"

        >>> Color.validate("red")     # True
        >>> Color.validate("yellow")  # False

    Order of inheritance matters — the mixin must come first.
    """

    @classmethod
    def validate(cls, value) -> bool:
        """Validate if a value is in the enum. True if so, False otherwise."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


# This Mixin will be removed in a future version. And has no effect from now on
class ExcludeEnumMixin:
    """(deprecated) Mixin to exclude enum from OpenAPI schema. We use this to avoid duplicating enums when generating client code from the openapi spec."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__.startswith("ExcludeEnumMixin"):
            warnings.warn(
                "The `ExcludeEnumMixin` class is deprecated. Should be removed from enums inheriting this class.",
                category=CrypticornDeprecatedSince28,
            )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        # schema.pop("enum", None)
        return schema


class ApiErrorFallback(EnumMeta):
    """Fallback for enum members that are not yet published to PyPI."""

    def __getattr__(cls, name):
        # Let Pydantic/internal stuff pass silently ! fragile
        if name.startswith("__") or name.startswith("_pytest"):
            raise AttributeError(name)
        _logger.warning(
            f"Unknown enum member '{name}' - update crypticorn package or check for typos"
        )
        return cls.UNKNOWN_ERROR
