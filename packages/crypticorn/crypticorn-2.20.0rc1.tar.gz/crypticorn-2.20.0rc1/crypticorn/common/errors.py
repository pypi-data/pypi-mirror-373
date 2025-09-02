"""Comprehensive error handling system defining various API error types, HTTP exceptions, and error content structures."""

from enum import Enum

from fastapi import status

from crypticorn.common.mixins import ApiErrorFallback

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum


class ApiErrorType(StrEnum):
    """Type of the API error."""

    USER_ERROR = "user error"
    """user error by people using our services"""
    EXCHANGE_ERROR = "exchange error"
    """re-tryable error by the exchange or network conditions"""
    SERVER_ERROR = "server error"
    """server error that needs a new version rollout for a fix"""
    NO_ERROR = "no error"
    """error that does not need to be handled or does not affect the program or is a placeholder."""


class ApiErrorLevel(StrEnum):
    """Level of the API error."""

    ERROR = "error"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"


class ApiErrorIdentifier(StrEnum):
    """Unique identifier of the API error."""

    ALLOCATION_BELOW_EXPOSURE = "allocation_below_current_exposure"
    ALLOCATION_BELOW_MINIMUM = "allocation_below_min_amount"
    ALLOCATION_LIMIT_EXCEEDED = "allocation_limit_exceeded"
    BLACK_SWAN = "black_swan"
    BOT_ALREADY_DELETED = "bot_already_deleted"
    BOT_STOPPING_COMPLETED = "bot_stopping_completed"
    BOT_STOPPING_STARTED = "bot_stopping_started"
    CANCELLED_OPEN_ORDER = "cancelled_open_order"
    CLIENT_ORDER_ID_REPEATED = "client_order_id_already_exists"
    CONTENT_TYPE_ERROR = "invalid_content_type"
    COUPON_APPLIED = "coupon_applied"
    COUPON_INVALID = "coupon_invalid"
    DELETE_BOT_ERROR = "delete_bot_error"
    EXCHANGE_HTTP_ERROR = "exchange_http_request_error"
    EXCHANGE_INVALID_PARAMETER = "exchange_invalid_parameter"
    EXCHANGE_INVALID_SIGNATURE = "exchange_invalid_signature"
    EXCHANGE_INVALID_TIMESTAMP = "exchange_invalid_timestamp"
    EXCHANGE_IP_RESTRICTED = "exchange_ip_address_is_not_authorized"
    EXCHANGE_KEY_ALREADY_EXISTS = "exchange_key_already_exists"
    EXCHANGE_KEY_IN_USE = "exchange_key_in_use"
    EXCHANGE_MAINTENANCE = "exchange_system_under_maintenance"
    EXCHANGE_RATE_LIMIT = "exchange_rate_limit_exceeded"
    EXCHANGE_PERMISSION_DENIED = "insufficient_permissions_spot_and_futures_required"
    EXCHANGE_SERVICE_UNAVAILABLE = "exchange_service_temporarily_unavailable"
    EXCHANGE_SYSTEM_BUSY = "exchange_system_is_busy"
    EXCHANGE_SYSTEM_CONFIG_ERROR = "exchange_system_configuration_error"
    EXCHANGE_SYSTEM_ERROR = "exchange_internal_system_error"
    EXCHANGE_USER_FROZEN = "exchange_user_account_is_frozen"
    EXPIRED_API_KEY = "api_key_expired"
    EXPIRED_BEARER = "bearer_token_expired"
    FAILED_OPEN_ORDER = "failed_open_order"
    FORBIDDEN = "forbidden"
    HEDGE_MODE_NOT_ACTIVE = "hedge_mode_not_active"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    INSUFFICIENT_MARGIN = "insufficient_margin"
    INSUFFICIENT_SCOPES = "insufficient_scopes"
    INVALID_API_KEY = "invalid_api_key"
    INVALID_BASIC_AUTH = "invalid_basic_auth"
    INVALID_BEARER = "invalid_bearer"
    INVALID_DATA_REQUEST = "invalid_data"
    INVALID_DATA_RESPONSE = "invalid_data_response"
    INVALID_EXCHANGE_KEY = "invalid_exchange_key"
    INVALID_MODEL_NAME = "invalid_model_name"
    LEVERAGE_EXCEEDED = "leverage_limit_exceeded"
    LIQUIDATION_PRICE_VIOLATION = "order_violates_liquidation_price_constraints"
    MARGIN_MODE_CLASH = "margin_mode_clash"
    NAME_NOT_UNIQUE = "name_not_unique"
    NO_CREDENTIALS = "no_credentials"
    NOW_API_DOWN = "now_api_down"
    OBJECT_ALREADY_EXISTS = "object_already_exists"
    OBJECT_CREATED = "object_created"
    OBJECT_DELETED = "object_deleted"
    OBJECT_LOCKED = "object_locked"
    OBJECT_NOT_FOUND = "object_not_found"
    OBJECT_UPDATED = "object_updated"
    ORDER_ALREADY_FILLED = "order_is_already_filled"
    ORDER_IN_PROCESS = "order_is_being_processed"
    ORDER_LIMIT_EXCEEDED = "order_quantity_limit_exceeded"
    ORDER_NOT_FOUND = "order_does_not_exist"
    ORDER_PRICE_INVALID = "order_price_is_invalid"
    ORDER_SIZE_TOO_LARGE = "order_size_too_large"
    ORDER_SIZE_TOO_SMALL = "order_size_too_small"
    ORPHAN_OPEN_ORDER = "orphan_open_order"
    ORPHAN_CLOSE_ORDER = "orphan_close_order"
    POSITION_LIMIT_EXCEEDED = "position_limit_exceeded"
    POSITION_NOT_FOUND = "position_does_not_exist"
    POSITION_SUSPENDED = "position_opening_temporarily_suspended"
    POST_ONLY_REJECTED = "post_only_order_would_immediately_match"
    REQUEST_SCOPE_EXCEEDED = "request_scope_limit_exceeded"
    RISK_LIMIT_EXCEEDED = "risk_limit_exceeded"
    RPC_TIMEOUT = "rpc_timeout"
    SETTLEMENT_IN_PROGRESS = "system_settlement_in_process"
    STRATEGY_DISABLED = "strategy_disabled"
    STRATEGY_LEVERAGE_MISMATCH = "strategy_leverage_mismatch"
    STRATEGY_NOT_SUPPORTING_EXCHANGE = "strategy_not_supporting_exchange"
    SUCCESS = "success"
    SYMBOL_NOT_FOUND = "symbol_does_not_exist"
    TRADING_ACTION_EXPIRED = "trading_action_expired"
    TRADING_ACTION_SKIPPED_BOT_STOPPING = "trading_action_skipped_bot_stopping"
    TRADING_LOCKED = "trading_has_been_locked"
    TRADING_SUSPENDED = "trading_is_suspended"
    UNKNOWN_ERROR = "unknown_error_occurred"
    URL_NOT_FOUND = "requested_resource_not_found"

    def get_error(self) -> "ApiError":
        """Get the corresponding ApiError."""
        return getattr(ApiError, self.name)


class ApiError(Enum, metaclass=ApiErrorFallback):
    # Fallback to UNKNOWN_ERROR for error codes not yet published to PyPI.
    """Crypticorn API error enumeration."""

    ALLOCATION_BELOW_EXPOSURE = (
        ApiErrorIdentifier.ALLOCATION_BELOW_EXPOSURE,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    ALLOCATION_BELOW_MINIMUM = (
        ApiErrorIdentifier.ALLOCATION_BELOW_MINIMUM,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    ALLOCATION_LIMIT_EXCEEDED = (
        ApiErrorIdentifier.ALLOCATION_LIMIT_EXCEEDED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.INFO,
    )
    BLACK_SWAN = (
        ApiErrorIdentifier.BLACK_SWAN,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.INFO,
    )
    BOT_ALREADY_DELETED = (
        ApiErrorIdentifier.BOT_ALREADY_DELETED,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.INFO,
    )
    BOT_STOPPING_COMPLETED = (
        ApiErrorIdentifier.BOT_STOPPING_COMPLETED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.SUCCESS,
    )
    BOT_STOPPING_STARTED = (
        ApiErrorIdentifier.BOT_STOPPING_STARTED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.SUCCESS,
    )
    CANCELLED_OPEN_ORDER = (
        ApiErrorIdentifier.CANCELLED_OPEN_ORDER,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.INFO,
    )
    CLIENT_ORDER_ID_REPEATED = (
        ApiErrorIdentifier.CLIENT_ORDER_ID_REPEATED,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    CONTENT_TYPE_ERROR = (
        ApiErrorIdentifier.CONTENT_TYPE_ERROR,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    COUPON_APPLIED = (
        ApiErrorIdentifier.COUPON_APPLIED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.SUCCESS,
    )
    COUPON_INVALID = (
        ApiErrorIdentifier.COUPON_INVALID,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    DELETE_BOT_ERROR = (
        ApiErrorIdentifier.DELETE_BOT_ERROR,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_HTTP_ERROR = (
        ApiErrorIdentifier.EXCHANGE_HTTP_ERROR,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_INVALID_PARAMETER = (
        ApiErrorIdentifier.EXCHANGE_INVALID_PARAMETER,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_INVALID_SIGNATURE = (
        ApiErrorIdentifier.EXCHANGE_INVALID_SIGNATURE,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_INVALID_TIMESTAMP = (
        ApiErrorIdentifier.EXCHANGE_INVALID_TIMESTAMP,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_IP_RESTRICTED = (
        ApiErrorIdentifier.EXCHANGE_IP_RESTRICTED,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_KEY_ALREADY_EXISTS = (
        ApiErrorIdentifier.EXCHANGE_KEY_ALREADY_EXISTS,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_KEY_IN_USE = (
        ApiErrorIdentifier.EXCHANGE_KEY_IN_USE,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_MAINTENANCE = (
        ApiErrorIdentifier.EXCHANGE_MAINTENANCE,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_RATE_LIMIT = (
        ApiErrorIdentifier.EXCHANGE_RATE_LIMIT,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_PERMISSION_DENIED = (
        ApiErrorIdentifier.EXCHANGE_PERMISSION_DENIED,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_SERVICE_UNAVAILABLE = (
        ApiErrorIdentifier.EXCHANGE_SERVICE_UNAVAILABLE,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_SYSTEM_BUSY = (
        ApiErrorIdentifier.EXCHANGE_SYSTEM_BUSY,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_SYSTEM_CONFIG_ERROR = (
        ApiErrorIdentifier.EXCHANGE_SYSTEM_CONFIG_ERROR,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_SYSTEM_ERROR = (
        ApiErrorIdentifier.EXCHANGE_SYSTEM_ERROR,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXCHANGE_USER_FROZEN = (
        ApiErrorIdentifier.EXCHANGE_USER_FROZEN,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXPIRED_API_KEY = (
        ApiErrorIdentifier.EXPIRED_API_KEY,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    EXPIRED_BEARER = (
        ApiErrorIdentifier.EXPIRED_BEARER,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    FAILED_OPEN_ORDER = (
        ApiErrorIdentifier.FAILED_OPEN_ORDER,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.INFO,
    )
    FORBIDDEN = (
        ApiErrorIdentifier.FORBIDDEN,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    HEDGE_MODE_NOT_ACTIVE = (
        ApiErrorIdentifier.HEDGE_MODE_NOT_ACTIVE,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INSUFFICIENT_BALANCE = (
        ApiErrorIdentifier.INSUFFICIENT_BALANCE,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INSUFFICIENT_MARGIN = (
        ApiErrorIdentifier.INSUFFICIENT_MARGIN,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INSUFFICIENT_SCOPES = (
        ApiErrorIdentifier.INSUFFICIENT_SCOPES,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INVALID_API_KEY = (
        ApiErrorIdentifier.INVALID_API_KEY,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INVALID_BASIC_AUTH = (
        ApiErrorIdentifier.INVALID_BASIC_AUTH,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INVALID_BEARER = (
        ApiErrorIdentifier.INVALID_BEARER,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INVALID_DATA_REQUEST = (
        ApiErrorIdentifier.INVALID_DATA_REQUEST,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INVALID_DATA_RESPONSE = (
        ApiErrorIdentifier.INVALID_DATA_RESPONSE,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INVALID_EXCHANGE_KEY = (
        ApiErrorIdentifier.INVALID_EXCHANGE_KEY,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    INVALID_MODEL_NAME = (
        ApiErrorIdentifier.INVALID_MODEL_NAME,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    LEVERAGE_EXCEEDED = (
        ApiErrorIdentifier.LEVERAGE_EXCEEDED,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    LIQUIDATION_PRICE_VIOLATION = (
        ApiErrorIdentifier.LIQUIDATION_PRICE_VIOLATION,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    MARGIN_MODE_CLASH = (
        ApiErrorIdentifier.MARGIN_MODE_CLASH,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    NAME_NOT_UNIQUE = (
        ApiErrorIdentifier.NAME_NOT_UNIQUE,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    NO_CREDENTIALS = (
        ApiErrorIdentifier.NO_CREDENTIALS,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    NOW_API_DOWN = (
        ApiErrorIdentifier.NOW_API_DOWN,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    OBJECT_ALREADY_EXISTS = (
        ApiErrorIdentifier.OBJECT_ALREADY_EXISTS,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    OBJECT_CREATED = (
        ApiErrorIdentifier.OBJECT_CREATED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.SUCCESS,
    )
    OBJECT_DELETED = (
        ApiErrorIdentifier.OBJECT_DELETED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.SUCCESS,
    )
    OBJECT_LOCKED = (
        ApiErrorIdentifier.OBJECT_LOCKED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.INFO,
    )
    OBJECT_NOT_FOUND = (
        ApiErrorIdentifier.OBJECT_NOT_FOUND,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    OBJECT_UPDATED = (
        ApiErrorIdentifier.OBJECT_UPDATED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.SUCCESS,
    )
    ORDER_ALREADY_FILLED = (
        ApiErrorIdentifier.ORDER_ALREADY_FILLED,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.INFO,
    )
    ORDER_IN_PROCESS = (
        ApiErrorIdentifier.ORDER_IN_PROCESS,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.INFO,
    )
    ORDER_LIMIT_EXCEEDED = (
        ApiErrorIdentifier.ORDER_LIMIT_EXCEEDED,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    ORDER_NOT_FOUND = (
        ApiErrorIdentifier.ORDER_NOT_FOUND,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    ORDER_PRICE_INVALID = (
        ApiErrorIdentifier.ORDER_PRICE_INVALID,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    ORDER_SIZE_TOO_LARGE = (
        ApiErrorIdentifier.ORDER_SIZE_TOO_LARGE,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.WARNING,
    )
    ORDER_SIZE_TOO_SMALL = (
        ApiErrorIdentifier.ORDER_SIZE_TOO_SMALL,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.WARNING,
    )
    ORPHAN_OPEN_ORDER = (
        ApiErrorIdentifier.ORPHAN_OPEN_ORDER,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.WARNING,
    )
    ORPHAN_CLOSE_ORDER = (
        ApiErrorIdentifier.ORPHAN_CLOSE_ORDER,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.WARNING,
    )
    POSITION_LIMIT_EXCEEDED = (
        ApiErrorIdentifier.POSITION_LIMIT_EXCEEDED,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    POSITION_NOT_FOUND = (
        ApiErrorIdentifier.POSITION_NOT_FOUND,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.WARNING,
    )
    POSITION_SUSPENDED = (
        ApiErrorIdentifier.POSITION_SUSPENDED,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    POST_ONLY_REJECTED = (
        ApiErrorIdentifier.POST_ONLY_REJECTED,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    REQUEST_SCOPE_EXCEEDED = (
        ApiErrorIdentifier.REQUEST_SCOPE_EXCEEDED,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    RISK_LIMIT_EXCEEDED = (
        ApiErrorIdentifier.RISK_LIMIT_EXCEEDED,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    RPC_TIMEOUT = (
        ApiErrorIdentifier.RPC_TIMEOUT,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    SETTLEMENT_IN_PROGRESS = (
        ApiErrorIdentifier.SETTLEMENT_IN_PROGRESS,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    STRATEGY_DISABLED = (
        ApiErrorIdentifier.STRATEGY_DISABLED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.WARNING,
    )
    STRATEGY_LEVERAGE_MISMATCH = (
        ApiErrorIdentifier.STRATEGY_LEVERAGE_MISMATCH,
        ApiErrorType.USER_ERROR,
        ApiErrorLevel.ERROR,
    )
    STRATEGY_NOT_SUPPORTING_EXCHANGE = (
        ApiErrorIdentifier.STRATEGY_NOT_SUPPORTING_EXCHANGE,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.WARNING,
    )
    SUCCESS = (ApiErrorIdentifier.SUCCESS, ApiErrorType.NO_ERROR, ApiErrorLevel.SUCCESS)
    SYMBOL_NOT_FOUND = (
        ApiErrorIdentifier.SYMBOL_NOT_FOUND,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    TRADING_ACTION_EXPIRED = (
        ApiErrorIdentifier.TRADING_ACTION_EXPIRED,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.INFO,
    )
    TRADING_ACTION_SKIPPED_BOT_STOPPING = (
        ApiErrorIdentifier.TRADING_ACTION_SKIPPED_BOT_STOPPING,
        ApiErrorType.NO_ERROR,
        ApiErrorLevel.INFO,
    )
    TRADING_LOCKED = (
        ApiErrorIdentifier.TRADING_LOCKED,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    TRADING_SUSPENDED = (
        ApiErrorIdentifier.TRADING_SUSPENDED,
        ApiErrorType.EXCHANGE_ERROR,
        ApiErrorLevel.ERROR,
    )
    UNKNOWN_ERROR = (
        ApiErrorIdentifier.UNKNOWN_ERROR,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )
    URL_NOT_FOUND = (
        ApiErrorIdentifier.URL_NOT_FOUND,
        ApiErrorType.SERVER_ERROR,
        ApiErrorLevel.ERROR,
    )

    @property
    def identifier(self) -> str:
        """Identifier of the error."""
        return self.value[0]

    @property
    def type(self) -> ApiErrorType:
        """Type of the error."""
        return self.value[1]

    @property
    def level(self) -> ApiErrorLevel:
        """Level of the error."""
        return self.value[2]

    @property
    def http_code(self) -> int:
        """HTTP status code for the error."""
        return StatusCodeMapper.get_http_code(self)

    @property
    def websocket_code(self) -> int:
        """WebSocket status code for the error."""
        return StatusCodeMapper.get_websocket_code(self)

    @classmethod
    def from_json(cls, data: dict) -> "ApiError":
        """Load an ApiError from a dictionary. Must contain the identifier with the key 'code'."""
        return next(error for error in cls if error.identifier == data["code"])


class StatusCodeMapper:
    """Mapping of API errors to HTTP/Websocket status codes."""

    _mapping = {
        # Authentication/Authorization
        ApiError.EXPIRED_BEARER: (
            status.HTTP_401_UNAUTHORIZED,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.INVALID_BASIC_AUTH: (
            status.HTTP_401_UNAUTHORIZED,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.INVALID_BEARER: (
            status.HTTP_401_UNAUTHORIZED,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXPIRED_API_KEY: (
            status.HTTP_401_UNAUTHORIZED,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.INVALID_API_KEY: (
            status.HTTP_401_UNAUTHORIZED,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.NO_CREDENTIALS: (
            status.HTTP_401_UNAUTHORIZED,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.INSUFFICIENT_SCOPES: (
            status.HTTP_403_FORBIDDEN,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_PERMISSION_DENIED: (
            status.HTTP_403_FORBIDDEN,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_USER_FROZEN: (
            status.HTTP_403_FORBIDDEN,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.TRADING_LOCKED: (
            status.HTTP_403_FORBIDDEN,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.FORBIDDEN: (
            status.HTTP_403_FORBIDDEN,
            status.WS_1008_POLICY_VIOLATION,
        ),
        # Not Found
        ApiError.URL_NOT_FOUND: (
            status.HTTP_404_NOT_FOUND,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.OBJECT_NOT_FOUND: (
            status.HTTP_404_NOT_FOUND,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORDER_NOT_FOUND: (
            status.HTTP_404_NOT_FOUND,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.POSITION_NOT_FOUND: (
            status.HTTP_404_NOT_FOUND,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.SYMBOL_NOT_FOUND: (
            status.HTTP_404_NOT_FOUND,
            status.WS_1008_POLICY_VIOLATION,
        ),
        # Conflicts/Duplicates
        ApiError.CLIENT_ORDER_ID_REPEATED: (
            status.HTTP_409_CONFLICT,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.OBJECT_ALREADY_EXISTS: (
            status.HTTP_409_CONFLICT,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_KEY_ALREADY_EXISTS: (
            status.HTTP_409_CONFLICT,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.BOT_ALREADY_DELETED: (
            status.HTTP_409_CONFLICT,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.NAME_NOT_UNIQUE: (
            status.HTTP_409_CONFLICT,
            status.WS_1008_POLICY_VIOLATION,
        ),
        # Invalid Content
        ApiError.CONTENT_TYPE_ERROR: (
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            status.WS_1003_UNSUPPORTED_DATA,
        ),
        ApiError.INVALID_DATA_REQUEST: (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
        ),
        ApiError.INVALID_DATA_RESPONSE: (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
        ),
        # Rate Limits
        ApiError.EXCHANGE_RATE_LIMIT: (
            status.HTTP_429_TOO_MANY_REQUESTS,
            status.WS_1013_TRY_AGAIN_LATER,
        ),
        ApiError.REQUEST_SCOPE_EXCEEDED: (
            status.HTTP_429_TOO_MANY_REQUESTS,
            status.WS_1013_TRY_AGAIN_LATER,
        ),
        # Server Errors
        ApiError.UNKNOWN_ERROR: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.WS_1011_INTERNAL_ERROR,
        ),
        ApiError.EXCHANGE_SYSTEM_ERROR: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.WS_1011_INTERNAL_ERROR,
        ),
        ApiError.NOW_API_DOWN: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.WS_1011_INTERNAL_ERROR,
        ),
        ApiError.RPC_TIMEOUT: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.WS_1011_INTERNAL_ERROR,
        ),
        # Service Unavailable
        ApiError.EXCHANGE_SERVICE_UNAVAILABLE: (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.WS_1011_INTERNAL_ERROR,
        ),
        ApiError.EXCHANGE_MAINTENANCE: (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.WS_1011_INTERNAL_ERROR,
        ),
        ApiError.EXCHANGE_SYSTEM_BUSY: (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.WS_1011_INTERNAL_ERROR,
        ),
        ApiError.SETTLEMENT_IN_PROGRESS: (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.WS_1011_INTERNAL_ERROR,
        ),
        ApiError.POSITION_SUSPENDED: (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.WS_1011_INTERNAL_ERROR,
        ),
        ApiError.TRADING_SUSPENDED: (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.WS_1011_INTERNAL_ERROR,
        ),
        # Bad Requests (400) - Invalid parameters or states
        ApiError.MARGIN_MODE_CLASH: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.INVALID_MODEL_NAME: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ALLOCATION_BELOW_EXPOSURE: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ALLOCATION_LIMIT_EXCEEDED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ALLOCATION_BELOW_MINIMUM: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.BLACK_SWAN: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.DELETE_BOT_ERROR: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_INVALID_SIGNATURE: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_INVALID_TIMESTAMP: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_IP_RESTRICTED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_KEY_IN_USE: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_SYSTEM_CONFIG_ERROR: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.HEDGE_MODE_NOT_ACTIVE: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_HTTP_ERROR: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.INSUFFICIENT_BALANCE: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.INSUFFICIENT_MARGIN: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.INVALID_EXCHANGE_KEY: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.EXCHANGE_INVALID_PARAMETER: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.LEVERAGE_EXCEEDED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.LIQUIDATION_PRICE_VIOLATION: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORDER_ALREADY_FILLED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORDER_IN_PROCESS: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORDER_LIMIT_EXCEEDED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORDER_PRICE_INVALID: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORDER_SIZE_TOO_LARGE: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORDER_SIZE_TOO_SMALL: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORPHAN_OPEN_ORDER: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.ORPHAN_CLOSE_ORDER: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.POSITION_LIMIT_EXCEEDED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.POST_ONLY_REJECTED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.RISK_LIMIT_EXCEEDED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.STRATEGY_DISABLED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.STRATEGY_LEVERAGE_MISMATCH: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.STRATEGY_NOT_SUPPORTING_EXCHANGE: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.TRADING_ACTION_EXPIRED: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.TRADING_ACTION_SKIPPED_BOT_STOPPING: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.COUPON_INVALID: (
            status.HTTP_400_BAD_REQUEST,
            status.WS_1008_POLICY_VIOLATION,
        ),
        # Success cases
        ApiError.SUCCESS: (status.HTTP_200_OK, status.WS_1000_NORMAL_CLOSURE),
        ApiError.BOT_STOPPING_COMPLETED: (
            status.HTTP_200_OK,
            status.WS_1000_NORMAL_CLOSURE,
        ),
        ApiError.BOT_STOPPING_STARTED: (
            status.HTTP_200_OK,
            status.WS_1000_NORMAL_CLOSURE,
        ),
        ApiError.OBJECT_CREATED: (
            status.HTTP_201_CREATED,
            status.WS_1000_NORMAL_CLOSURE,
        ),
        ApiError.OBJECT_UPDATED: (status.HTTP_200_OK, status.WS_1000_NORMAL_CLOSURE),
        ApiError.OBJECT_DELETED: (
            status.HTTP_204_NO_CONTENT,
            status.WS_1000_NORMAL_CLOSURE,
        ),
        ApiError.CANCELLED_OPEN_ORDER: (
            status.HTTP_200_OK,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.FAILED_OPEN_ORDER: (
            status.HTTP_200_OK,
            status.WS_1008_POLICY_VIOLATION,
        ),
        ApiError.COUPON_APPLIED: (
            status.HTTP_200_OK,
            status.WS_1000_NORMAL_CLOSURE,
        ),
        # Miscellaneous
        ApiError.OBJECT_LOCKED: (
            status.HTTP_423_LOCKED,
            status.WS_1013_TRY_AGAIN_LATER,
        ),
    }

    @classmethod
    def get_http_code(cls, error: ApiError) -> int:
        """Get the HTTP status code for the error. If the error is not in the mapping, return 500."""
        return cls._mapping.get(error, cls._mapping[ApiError.UNKNOWN_ERROR])[0]

    @classmethod
    def get_websocket_code(cls, error: ApiError) -> int:
        """Get the WebSocket status code for the error. If the error is not in the mapping, return 1008."""
        return cls._mapping.get(error, cls._mapping[ApiError.UNKNOWN_ERROR])[1]
