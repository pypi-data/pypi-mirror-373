import asyncio
import inspect
import logging
import time
from functools import wraps
from typing import Any, Callable, Tuple, Type, Union

logger = logging.getLogger(__name__)

Ex = Union[Type[BaseException], Tuple[Type[BaseException], ...]]
Func = Callable[..., Any]


def retries(
    count: int = 5,
    wait_seconds: int = 5,
    catch: Ex = Exception,
    nocatch: Ex = (),
    warn: bool = True,
) -> Callable[[Func], Func]:
    """
    Decorator that retries a function (sync or async) if it raises exceptions.
    """

    def should_retry(ex: Exception) -> bool:
        return isinstance(ex, catch) and not isinstance(ex, nocatch)

    def log_fail(attempt: int, func: Func, ex: Exception) -> None:
        if warn:
            logger.warning(
                f"Failed attempt={attempt} to call {func.__name__} "
                f"( {type(ex).__name__}: {ex} )"
            )

    def decorator(func: Func) -> Func:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                for attempt in range(1, count + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as ex:
                        if not should_retry(ex) or attempt == count:
                            raise
                        log_fail(attempt, func, ex)
                        await asyncio.sleep(wait_seconds)

            return async_wrapper  # type: ignore

        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                for attempt in range(1, count + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as ex:
                        if not should_retry(ex) or attempt == count:
                            raise
                        log_fail(attempt, func, ex)
                        time.sleep(wait_seconds)

            return sync_wrapper  # type: ignore

    return decorator
