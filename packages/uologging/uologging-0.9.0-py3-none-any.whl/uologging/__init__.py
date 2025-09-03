from warnings import warn

from uologging import format
from uologging.cli import add_verbosity_flag, get_default_parser
from uologging.downloads import DownloadTracer
from uologging.performance import trace
from uologging.uologging import init_console, init_syslog, set_verbosity


def function_renamed(function, old_name):
    """Want to change the name of some function in your python library?
    But you don't want to break your users' code?

    This function will wrap any function with a deprecated alias.

    Example:

    Imagine you have the 'say_hello' function in your library.

        >>> def say_hello():
        ...     print('Hello, world!')

    You want to change the name to 'hello,' and so you do!

        >>> def hello():
        ...     print('Hello, world!')

    But, you don't want to break your users' code.


        >>> say_hello = function_renamed(hello, 'say_hello')
        >>> __all__ = ['hello', 'say_hello']


    Args:
        new_function (_type_): _description_
        deprecated_function_name (_type_): _description_
    """

    def deprecated_function(*args, **kwargs):
        deprecation_warning = f"{old_name}() is deprecated (we plan to remove it in next major-version). Please use {function.__name__}() instead."
        warn(deprecation_warning, DeprecationWarning, stacklevel=2)
        # NOW, only after warning, pass on to the underlying function
        function(*args, **kwargs)

    return deprecated_function


init_console_logging = function_renamed(init_console, old_name="init_console_logging")
init_syslog_logging = function_renamed(init_syslog, old_name="init_syslog_logging")
set_logging_verbosity = function_renamed(
    set_verbosity, old_name="set_logging_verbosity"
)

__version__ = "0.9.0"
__all__ = [
    "add_verbosity_flag",
    "DownloadTracer",
    "format",
    "get_default_parser",
    "init_console_logging",
    "init_console",
    "init_syslog_logging",
    "init_syslog",
    "set_logging_verbosity",
    "set_verbosity",
    "trace",
]
