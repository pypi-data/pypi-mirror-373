from _typeshed import Incomplete
from typing import Any

class BaseInvokerError(Exception):
    """Base exception class for all gllm_inference invoker errors."""
    debug_info: Incomplete
    class_name: Incomplete
    def __init__(self, class_name: str, message: str, debug_info: dict[str, Any] | None = None) -> None:
        """Initialize the base exception.

        Args:
            class_name (str): The name of the class that raised the error.
            message (str): The error message.
            debug_info (dict[str, Any] | None, optional): Additional debug information for developers.
                Defaults to None.
        """
    def verbose(self) -> str:
        """Verbose error message with debug information.

        Returns:
            str: The verbose error message with debug information.
        """

class ProviderInvalidArgsError(BaseInvokerError):
    """Exception for bad or malformed requests, invalid parameters or structure.

    Corresponds to HTTP 400 status code.
    """
    def __init__(self, class_name: str, debug_info: dict[str, Any] | None = None) -> None:
        """Initialize ProviderInvalidArgsError.

        Args:
            class_name (str): The name of the class that raised the error.
            debug_info (dict[str, Any] | None, optional): Additional debug information for developers.
                Defaults to None.
        """

class ProviderAuthError(BaseInvokerError):
    """Exception for authorization failures due to API key issues.

    Corresponds to HTTP 401-403 status codes.
    """
    def __init__(self, class_name: str, debug_info: dict[str, Any] | None = None) -> None:
        """Initialize ProviderAuthError.

        Args:
            class_name (str): The name of the class that raised the error.
            debug_info (dict[str, Any] | None, optional): Additional debug information for developers.
                Defaults to None.
        """

class ProviderRateLimitError(BaseInvokerError):
    """Exception for rate limit violations.

    Corresponds to HTTP 429 status code.
    """
    def __init__(self, class_name: str, debug_info: dict[str, Any] | None = None) -> None:
        """Initialize ProviderRateLimitError.

        Args:
            class_name (str): The name of the class that raised the error.
            debug_info (dict[str, Any] | None, optional): Additional debug information for developers.
                Defaults to None.
        """

class ProviderInternalError(BaseInvokerError):
    """Exception for unexpected server-side errors.

    Corresponds to HTTP 500 status code.
    """
    def __init__(self, class_name: str, debug_info: dict[str, Any] | None = None) -> None:
        """Initialize ProviderInternalError.

        Args:
            class_name (str): The name of the class that raised the error.
            debug_info (dict[str, Any] | None, optional): Additional debug information for developers.
                Defaults to None.
        """

class ProviderOverloadedError(BaseInvokerError):
    """Exception for when the engine is currently overloaded.

    Corresponds to HTTP 503, 529 status codes.
    """
    def __init__(self, class_name: str, debug_info: dict[str, Any] | None = None) -> None:
        """Initialize ProviderOverloadedError.

        Args:
            class_name (str): The name of the class that raised the error.
            debug_info (dict[str, Any] | None, optional): Additional debug information for developers.
                Defaults to None.
        """

class ModelNotFoundError(BaseInvokerError):
    """Exception for model not found errors.

    Corresponds to HTTP 404 status code.
    """
    def __init__(self, class_name: str, debug_info: dict[str, Any] | None = None) -> None:
        """Initialize ModelNotFoundError.

        Args:
            class_name (str): The name of the class that raised the error.
            debug_info (dict[str, Any] | None, optional): Additional debug information for developers.
                Defaults to None.
        """

class InvokerRuntimeError(BaseInvokerError):
    """Exception for runtime errors that occur during the invocation of the model.

    Corresponds to HTTP status codes other than the ones defined in HTTP_STATUS_TO_EXCEPTION_MAP.
    """
    def __init__(self, class_name: str, debug_info: dict[str, Any] | None = None) -> None:
        """Initialize the InvokerRuntimeError.

        Args:
            class_name (str): The name of the class that raised the error.
            debug_info (dict[str, Any] | None, optional): Additional debug information for developers.
                Defaults to None.
        """
