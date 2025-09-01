from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from dj_raincheck.store import function_queue


def raincheck(func: Callable | None = None, **raincheck_kwargs):
    """Decorator to defer function execution until after the HTTP response is sent. The decorated
    function will have a `schedule()` method that can be called to queue the function for execution.
    """

    if "dj_raincheck" not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("'dj_raincheck' must be in INSTALLED_APPS")

    def decorator(_func: Callable) -> Any:
        def schedule(*args, **kwargs):
            if getattr(settings, "RAINCHECK_IMMEDIATE", False):
                return _func(*args, **kwargs)

            function_queue.append((_func, args, kwargs))

        _func.__raincheck = raincheck_kwargs  # type: ignore
        _func.schedule = schedule  # type: ignore

        return _func

    if func is None:
        return decorator

    return decorator(func)
