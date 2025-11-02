import asyncio
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any

from gspace.utils.logger import get_logger


class RetryStrategy(Enum):
    """Retry strategies for failed requests."""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CONSTANT_BACKOFF = "constant_backoff"
    RANDOM_BACKOFF = "random_backoff"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_second: int = 10
    burst_limit: int = 20
    window_size: float = 1.0  # seconds
    retry_after_header: str = "Retry-After"
    quota_exceeded_codes: list[int] = field(default_factory=lambda: [429, 503])


@dataclass
class RetryConfig:
    """Configuration for retry logic."""

    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    retryable_errors: list[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )


class RateLimiter:
    """
    Token bucket rate limiter for Google API requests.
    Implements sliding window rate limiting with burst support.
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize the rate limiter.

        Args:
            config: Rate limiting configuration
        """
        self.config = config
        self.logger = get_logger("gspace.rate_limiter")

        # Token bucket state
        self.tokens = config.burst_limit
        self.last_refill = time.time()
        self.window_start = time.time()
        self.request_count = 0

        self.logger.info(
            f"RateLimiter initialized: {config.requests_per_second} req/s, burst: {config.burst_limit}"
        )

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        time_passed = now - self.last_refill

        if time_passed >= self.config.window_size:
            # Calculate new tokens
            new_tokens = int(time_passed * self.config.requests_per_second)
            self.tokens = min(self.config.burst_limit, self.tokens + new_tokens)
            self.last_refill = now

            # Reset window if needed
            if now - self.window_start >= self.config.window_size:
                self.window_start = now
                self.request_count = 0

    def acquire_token(self, timeout: float | None = None) -> bool:
        """
        Acquire a token for making a request.

        Args:
            timeout: Maximum time to wait for a token

        Returns:
            True if token acquired, False if timeout
        """
        start_time = time.time()

        while True:
            self._refill_tokens()

            if self.tokens > 0:
                self.tokens -= 1
                self.request_count += 1
                return True

            # Check timeout
            if timeout is not None and (time.time() - start_time) >= timeout:
                self.logger.warning("Rate limit token acquisition timeout")
                return False

            # Wait for next refill
            time.sleep(0.1)

    def wait_for_token(self) -> None:
        """Wait until a token is available."""
        while not self.acquire_token():
            time.sleep(0.1)

    def get_wait_time(self) -> float:
        """
        Calculate time to wait for next available token.

        Returns:
            Time to wait in seconds
        """
        self._refill_tokens()

        if self.tokens > 0:
            return 0.0

        # Calculate time until next refill
        time_since_refill = time.time() - self.last_refill
        time_until_refill = self.config.window_size - time_since_refill

        if time_until_refill <= 0:
            return 0.0

        # Calculate tokens needed and time to wait
        tokens_needed = 1
        time_to_wait = tokens_needed / self.config.requests_per_second

        return max(0.0, time_to_wait)

    def get_stats(self) -> dict[str, Any]:
        """
        Get current rate limiter statistics.

        Returns:
            Dictionary with rate limiter stats
        """
        self._refill_tokens()

        return {
            "available_tokens": self.tokens,
            "max_tokens": self.config.burst_limit,
            "requests_per_second": self.config.requests_per_second,
            "window_start": self.window_start,
            "request_count": self.request_count,
            "wait_time": self.get_wait_time(),
        }


class RetryHandler:
    """
    Handles retry logic for failed API requests.
    Supports multiple retry strategies and exponential backoff.
    """

    def __init__(self, config: RetryConfig):
        """
        Initialize the retry handler.

        Args:
            config: Retry configuration
        """
        self.config = config
        self.logger = get_logger("gspace.retry_handler")

        self.logger.info(
            f"RetryHandler initialized: max_retries={config.max_retries}, strategy={config.strategy.value}"
        )

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a retry attempt.

        Args:
            attempt: Current attempt number (1-based)

        Returns:
            Delay in seconds
        """
        if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (2 ** (attempt - 1))
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt
        elif self.config.strategy == RetryStrategy.CONSTANT_BACKOFF:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.RANDOM_BACKOFF:
            delay = random.uniform(0, self.config.base_delay * (2 ** (attempt - 1)))
        else:
            delay = self.config.base_delay

        # Apply jitter if enabled
        if self.config.jitter:
            jitter_factor = random.uniform(0.8, 1.2)
            delay *= jitter_factor

        # Cap delay to maximum
        return min(delay, self.config.max_delay)

    def should_retry(self, error: Exception, status_code: int | None = None) -> bool:
        """
        Determine if a request should be retried.

        Args:
            error: Exception that occurred
            status_code: HTTP status code if available

        Returns:
            True if request should be retried
        """
        # Check status code first
        if status_code and status_code in self.config.retryable_errors:
            return True

        # Check error type
        retryable_error_types = (
            ConnectionError,
            TimeoutError,
            OSError,
            Exception,  # Generic fallback
        )

        return isinstance(error, retryable_error_types)

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception after all retries exhausted
        """
        last_exception = None

        for attempt in range(
            1, self.config.max_retries + 2
        ):  # +2 because first attempt is not a retry
            try:
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # Check if we should retry
                if attempt > self.config.max_retries or not self.should_retry(e):
                    self.logger.error(f"Request failed after {attempt} attempts: {e}")
                    raise e

                # Calculate delay and wait
                delay = self._calculate_delay(attempt)
                self.logger.warning(
                    f"Request failed (attempt {attempt}/{self.config.max_retries + 1}), "
                    f"retrying in {delay:.2f}s: {e}"
                )

                time.sleep(delay)

        # This should never be reached, but just in case
        raise last_exception

    async def execute_with_retry_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function with retry logic.

        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception after all retries exhausted
        """
        last_exception = None

        for attempt in range(1, self.config.max_retries + 2):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # Check if we should retry
                if attempt > self.config.max_retries or not self.should_retry(e):
                    self.logger.error(
                        f"Async request failed after {attempt} attempts: {e}"
                    )
                    raise e

                # Calculate delay and wait
                delay = self._calculate_delay(attempt)
                self.logger.warning(
                    f"Async request failed (attempt {attempt}/{self.config.max_retries + 1}), "
                    f"retrying in {delay:.2f}s: {e}"
                )

                await asyncio.sleep(delay)

        raise last_exception


def rate_limited(rate_limiter: RateLimiter):
    """
    Decorator to apply rate limiting to functions.

    Args:
        rate_limiter: RateLimiter instance to use

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            rate_limiter.wait_for_token()
            return func(*args, **kwargs)

        return wrapper

    return decorator


def retry_on_failure(retry_config: RetryConfig):
    """
    Decorator to apply retry logic to functions.

    Args:
        retry_config: RetryConfig instance to use

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        retry_handler = RetryHandler(retry_config)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_handler.execute_with_retry(func, *args, **kwargs)

        return wrapper

    return decorator


def async_retry_on_failure(retry_config: RetryConfig):
    """
    Decorator to apply retry logic to async functions.

    Args:
        retry_config: RetryConfig instance to use

    Returns:
        Decorated async function
    """

    def decorator(func: Callable) -> Callable:
        retry_handler = RetryHandler(retry_config)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_handler.execute_with_retry_async(func, *args, **kwargs)

        return wrapper

    return decorator


class APIRateLimiter:
    """
    Combined rate limiter and retry handler for Google API requests.
    Provides a unified interface for managing API quotas and failures.
    """

    def __init__(self, rate_limit_config: RateLimitConfig, retry_config: RetryConfig):
        """
        Initialize the API rate limiter.

        Args:
            rate_limit_config: Rate limiting configuration
            retry_config: Retry configuration
        """
        self.rate_limiter = RateLimiter(rate_limit_config)
        self.retry_handler = RetryHandler(retry_config)
        self.logger = get_logger("gspace.api_rate_limiter")

        self.logger.info("APIRateLimiter initialized")

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with rate limiting and retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        # First, wait for rate limit token
        self.rate_limiter.wait_for_token()

        # Then execute with retry logic
        return self.retry_handler.execute_with_retry(func, *args, **kwargs)

    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function with rate limiting and retry logic.

        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        # First, wait for rate limit token
        self.rate_limiter.wait_for_token()

        # Then execute with retry logic
        return await self.retry_handler.execute_with_retry_async(func, *args, **kwargs)

    def get_stats(self) -> dict[str, Any]:
        """
        Get combined statistics from rate limiter and retry handler.

        Returns:
            Dictionary with combined stats
        """
        stats = {
            "rate_limiter": self.rate_limiter.get_stats(),
            "retry_config": {
                "max_retries": self.retry_handler.config.max_retries,
                "strategy": self.retry_handler.config.strategy.value,
                "base_delay": self.retry_handler.config.base_delay,
                "max_delay": self.retry_handler.config.max_delay,
            },
        }

        return stats
