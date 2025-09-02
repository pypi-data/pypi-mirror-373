import pytest

from crypticorn.common import ApiError, ApiErrorIdentifier, StatusCodeMapper


@pytest.mark.asyncio
async def test_lengths():
    """Checks that the enums have the same length and prints missing members if they don't."""
    try:
        assert len(list(ApiError)) == len(
            list(ApiErrorIdentifier)
        ), f"ApiError ({len(list(ApiError))}) and ApiErrorIdentifier ({len(list(ApiErrorIdentifier))}) do not have the same number of elements. Check above for missing members."
        assert len(list(ApiError)) == len(
            list(StatusCodeMapper._mapping.keys())
        ), f"ApiError ({len(list(ApiError))}) and StatusCodeMapper ({len(list(StatusCodeMapper._mapping.keys()))}) do not have the same number of elements. Check above for missing members."
    except AssertionError as e:
        # Helper for identifying missing members
        api_error_set = set(e.name for e in ApiError)
        api_error_identifier_set = set(e.name for e in ApiErrorIdentifier)
        http_status_mapper_set = set(
            h.name for h in list(StatusCodeMapper._mapping.keys())
        )

        print(
            "Missing in ApiErrorIdentifier:", api_error_set - api_error_identifier_set
        )
        print("Missing in ApiError:", api_error_identifier_set - api_error_set)
        print("Missing in StatusCodeMapper:", http_status_mapper_set - api_error_set)
        raise e


@pytest.mark.asyncio
async def test_enum_values():
    """Checks that the enums are string enums"""
    assert (
        ApiError.ALLOCATION_BELOW_MINIMUM.identifier
        == ApiErrorIdentifier.ALLOCATION_BELOW_MINIMUM
    ), "String enum values do not match"


@pytest.mark.asyncio
async def test_sorted():
    """Checks that the enums are sorted"""
    for error, identifier in zip(list(ApiError), list(ApiErrorIdentifier)):
        assert (
            error.identifier == identifier
        ), f"ApiError.{error.name} != ApiErrorIdentifier.{identifier.name}"


@pytest.mark.asyncio
async def test_fallback():
    """Checks that the fallback error is used when the error is not found due to a typo or not publishing the latest version of the client"""
    assert (
        ApiError.NOT_EXISTING_ERROR == ApiError.UNKNOWN_ERROR
    ), "Fallback error is not used"


@pytest.mark.asyncio
async def test_error_from_identifier():
    """Checks that the error can be retrieved from the identifier"""
    assert (
        ApiErrorIdentifier.ALLOCATION_BELOW_EXPOSURE.get_error()
        == ApiError.ALLOCATION_BELOW_EXPOSURE
    )
