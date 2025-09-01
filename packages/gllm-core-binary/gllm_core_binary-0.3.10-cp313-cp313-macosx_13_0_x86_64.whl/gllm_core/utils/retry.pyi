from _typeshed import Incomplete
from gllm_core.utils import LoggerManager as LoggerManager
from pydantic import BaseModel
from typing import Any, Callable, TypeVar

logger: Incomplete
T = TypeVar('T')
BASE_EXPONENTIAL_BACKOFF: float

class RetryConfig(BaseModel):
    """Configuration for retry behavior.

    Attributes:
        max_retries (int): Maximum number of retry attempts.
        base_delay (float): Base delay in seconds between retries.
        max_delay (float): Maximum delay in seconds between retries.
        exponential_base (float): Base for exponential backoff.
        jitter (bool): Whether to add random jitter to delays.
        timeout (float): Overall timeout in seconds for the entire operation. When set to 0.0, timeout is disabled.
        retry_on_exceptions (tuple[type[Exception], ...]): Tuple of exception types to retry on.
    """
    max_retries: int
    base_delay: float
    max_delay: float
    exponential_base: float
    jitter: bool
    timeout: float
    retry_on_exceptions: tuple[type[Exception], ...]
    def validate_delay_constraints(self) -> RetryConfig:
        """Validates that max_delay is greater than or equal to base_delay.

        Returns:
            RetryConfig: The validated configuration.

        Raises:
            ValueError: If max_delay is less than base_delay.
        """

async def retry(func: Callable[..., Any], *args: Any, retry_config: RetryConfig | None = None, **kwargs: Any) -> T:
    """Executes a function with retry logic and exponential backoff.

    This function executes the provided function with retry logic. It will first try to execute the function once.
    If the function raises an exception that matches the retry_on_exceptions, it will retry up to max_retries times
    with exponential backoff. Therefore, the max number of attempts is max_retries + 1. If provided, the timeout
    applies to the entire retry operation, including all attempts and delays.

    Example:
        If you set timeout=10s and max_retries=3, the entire retry operation (including all attempts
        and delays) will timeout after 10 seconds, not 10 seconds per attempt.

    Args:
        func (Callable[..., Any]): The function to execute.
        *args (Any): Positional arguments to pass to the function.
        retry_config (RetryConfig | None, optional): Retry configuration. If None, uses default config.
            Defaults to None.
        **kwargs (Any): Keyword arguments to pass to the function.

    Returns:
        T: The result of the function execution.

    Raises:
        Exception: The last exception raised by the function if all retries are exhausted.
        asyncio.TimeoutError: If the overall timeout is exceeded.
    """
