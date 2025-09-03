import sentry_sdk
from functools import wraps
from typing import Callable, Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

def initialize_sentry(dsn: str, environment: str = 'dev') -> None:
    if not sentry_sdk.Hub.current.client: 
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
        )

def track_exceptions(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_sdk.flush()
            raise
    return wrapper  # type: ignore
