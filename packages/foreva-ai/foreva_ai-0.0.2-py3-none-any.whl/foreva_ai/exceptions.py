"""
Foreva AI SDK Exceptions
Clean error handling for the SDK
"""


class ForevaError(Exception):
    """Base exception for all Foreva SDK errors"""
    pass


class ForevaAPIError(ForevaError):
    """API request failed"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class ForevaValidationError(ForevaError):
    """Input validation failed"""
    pass


class ForevaAuthenticationError(ForevaAPIError):
    """API key is invalid or missing"""
    pass


class ForevaNotFoundError(ForevaAPIError):
    """Resource not found"""
    pass


class ForevaRateLimitError(ForevaAPIError):
    """Rate limit exceeded"""
    pass


class ForevaTestLimitError(ForevaAPIError):
    """Test mode limits exceeded (daily or monthly)"""
    pass


class ForevaSubscriptionRequiredError(ForevaAPIError):
    """Live mode requires active subscription"""
    pass


class ForevaNetworkError(ForevaError):
    """Network connection failed"""
    pass