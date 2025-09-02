from enum import IntEnum

import pytest

from crypticorn.common.enums import MarketType, ValidateEnumMixin


class MockInt(ValidateEnumMixin, IntEnum):
    SPOT = 1
    FUTURES = 2


@pytest.fixture
def int_enum() -> MockInt:
    return MockInt


def test_str_enum_validation():
    """Test that the enum validation works"""
    # Test valid string values
    assert MarketType.validate("spot") is True
    assert MarketType.validate("futures") is True

    # Test invalid string values
    assert MarketType.validate("SPOT") is False
    assert MarketType.validate("invalid") is False

    # Test enum values
    assert MarketType.validate(MarketType.SPOT) is True
    assert MarketType.validate(MarketType.FUTURES) is True

    # Test enum construction
    assert MarketType("spot") == MarketType.SPOT
    assert MarketType("futures") == MarketType.FUTURES

    # Test invalid enum construction
    with pytest.raises(ValueError):
        MarketType("SPOT")
    with pytest.raises(ValueError):
        MarketType("invalid")


def test_int_enum_validation(int_enum):
    """Test that the enum validation works"""
    assert int_enum.validate(int_enum.SPOT) is True
    assert int_enum.validate(int_enum.FUTURES) is True
