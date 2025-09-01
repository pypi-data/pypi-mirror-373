import logging
import threading
from collections.abc import Callable

from django.conf import settings
from django.core.signals import request_finished

from dj_raincheck.store import function_queue

logger = logging.getLogger(__name__)


def execute_function(func: Callable, *args, **kwargs) -> None:
    """Execute a function with the given args and kwargs.

    This safely executes functions that were queued to run after the HTTP response has been sent.
    Any exceptions raised during execution will be caught and logged, but will not propagate to the caller.
    """
    try:
        func(*args, **kwargs)
    except Exception as e:
        logger.exception(e)


def execute_all_queued_functions(sender, **kwargs) -> None:  # noqa: ARG001
    """Process all functions in the queue after the `request_finished` signal is fired (which happens
    after the HTTP response has been sent).

    When running asynchronously, each function is executed in a separate daemon thread. Exceptions in
    queued functions are caught and logged but do not affect the main request/response cycle.
    """

    while len(function_queue):
        (func, args, kwargs) = function_queue.popleft()

        if getattr(settings, "RAINCHECK_RUN_ASYNC", True):
            threading.Thread(target=execute_function, args=(func, *args), kwargs=kwargs).start()
        else:
            execute_function(func, *args, **kwargs)


request_finished.connect(execute_all_queued_functions)
