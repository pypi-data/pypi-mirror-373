"""Network configuration mixin for feed classes."""

import typing as t


class NetworkConfigMixin:
    """Mixin that provides default implementations of network configuration properties.

    This class provides concrete implementations of the abstract network properties
    defined in AbstractFeed. Feeds can inherit from this mixin to get default
    implementations rather than implementing these properties individually.
    """

    NETWORK_CONFIG_KWARGS: t.ClassVar[list[str]] = ["timeout", "max_retries", "retry_delay", "api_key"]

    @classmethod
    def separate_network_kwargs(cls, kwargs: dict[str, t.Any]) -> tuple[dict[str, t.Any], dict[str, t.Any]]:
        """Separate network configuration parameters from other parameters.

        :param kwargs: Dictionary of keyword arguments

        :return: Tuple of (network_kwargs, other_kwargs)

        """
        network_kwargs = {}
        other_kwargs = {}
        for key, value in kwargs.items():
            if key in cls.NETWORK_CONFIG_KWARGS:
                network_kwargs[key] = value
            else:
                other_kwargs[key] = value

        return network_kwargs, other_kwargs

    def __init__(
        self: t.Self,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        api_key: str | None = None,
    ) -> None:
        """Initialize network configuration.

        :param timeout: Network timeout in seconds
        :param max_retries: Maximum number of retries for failed requests
        :param retry_delay: Delay between retries in seconds
        :param api_key: API key for authentication
        """
        # Don't call super().__init__() in a mixin - let the concrete class handle initialization order
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._api_key = api_key

    @property
    def timeout(self: t.Self) -> float:
        """Get timeout in seconds for network operations."""
        return self._timeout

    @timeout.setter
    def timeout(self: t.Self, value: float) -> None:
        """Set timeout in seconds for network operations."""
        self._timeout = value

    @property
    def max_retries(self: t.Self) -> int:
        """Get maximum number of retries for network operations."""
        return self._max_retries

    @max_retries.setter
    def max_retries(self: t.Self, value: int) -> None:
        """Set maximum number of retries for network operations."""
        self._max_retries = value

    @property
    def retry_delay(self: t.Self) -> float:
        """Get delay between retries in seconds."""
        return self._retry_delay

    @retry_delay.setter
    def retry_delay(self: t.Self, value: float) -> None:
        """Set delay between retries in seconds."""
        self._retry_delay = value

    @property
    def api_key(self: t.Self) -> str | None:
        """Get API key for authentication."""
        return self._api_key

    @api_key.setter
    def api_key(self: t.Self, value: str | None) -> None:
        """Set API key for authentication."""
        self._api_key = value
