import logging
import sys
import time
from functools import wraps

MAJOR = 0
MINOR = 1


def pretty_function_with_args_str(func, args, kwargs):
    return f'{func.__module__}:{func.__name__}({pretty_args(args, kwargs)})'


def pretty_args(args, kwargs):
    strings = []
    if args:
        strings.extend([repr(arg) for arg in args])
    if kwargs:
        strings.extend([f'{key}={repr(val)}' for key, val in kwargs.items()])
    return ', '.join(strings)


def pretty_function_no_args_str(func):
    return f'{func.__module__}:{func.__name__}(...)'


def trace(logger: logging.Logger, capture_args=True, level=logging.DEBUG):
    """Decorator to trace the execution time of a Python function or method.

    Uses INFO log level for logging the traced function's "exec time".
    Also will log the traced function's entry and exit at DEBUG log level.

    Args:
        logger (logging.Logger): The logger instance for the function's module.
        capture_args (bool, optional): When tracing the function, capture the 
            arguments provided to the function and add them to the log message.
            Defaults to True.

    Example:

    First, get the logger for your Python module.

        import logging
        logger = logging.getLogger(__name__)

    Then, use the trace_time decorator with that logger as the argument.

        import uologging
        @uologging.trace(logger)
        def my_slow_function():
            import time
            time.sleep(1)
        my_slow_function()
    """
    def _trace_time(func):
        def log_with_accurate_line_no(msg):
            if sys.version_info[MAJOR] >= 3 and sys.version_info[MINOR] >= 8:
                logger.log(msg=msg, stacklevel=3, level=level)
            else:
                logger.log(msg=msg, level=level)
        @wraps(func)
        def timed(*args, **kwargs):
            if capture_args:
                function_str = pretty_function_with_args_str(func, args, kwargs)
            else:
                function_str = pretty_function_no_args_str(func)
            log_with_accurate_line_no(f'Starting: {function_str}')
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            log_with_accurate_line_no(f'Finished: {function_str}')
            log_with_accurate_line_no(f'{function_str} exec time: {end - start:.2f} sec')
            return result
        return timed
    return _trace_time
