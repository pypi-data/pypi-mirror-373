UOLogging is a solution for configuring Python's built-in logging module, including a utility for tracing multithreaded downloads.

# Install

```
pip install uologging[optional]
```

> ℹ Use the '`[optional]` suffix to download the (†very small)  `humanize` package as well.
>
>> `humanize` makes logs human-readable when dealing with large numbers.
>>
>> † The `humanize` package is 78.5 kB as of version 4.9.0.

## Enable console logging

Simply call "`init_console()`" to initializing Python's root logger to log to console:

    # ⚠ Inadvisable: Enable logging for ALL python packages/modules
    uologging.init_console()

> ⚠ WARNING: It is inadvisable to "init" the overall root logger except for debugging. 
> Why? The console can get *very noisy* when using 3rd party libraries (that use Python `logging` module).

In general, you will want to specify your package name. To enable logging within your package only, you can provide your package name.

> The handy invocation of `__name__.split('.')[0]` will provide your package's name from *anywhere within your package*.

    # ✅ Best Practice: Enable logging only for your package.
    my_package_name = __name__.split('.')[0]
    uologging.init_console(my_package_name)


## Enable (Linux) syslog logging

Similarly, you can call "`init_syslog()`":

    # Best Practice: Enable logging for your python package
    my_package_name = __name__.split('.')[0]
    uologging.init_syslog(my_package_name)

    # Inadvisable: Enable logging for ALL python packages/modules
    uologging.init_syslog()


## Set Logging Verbosity

> Per Python logging suggestion: WARNING, ERROR, and CRITICAL messages are all logged by default.

If you are interested in seeing the DEBUG and INFO log messages, you'll need to update the logging verbosity in your application.
We provide the method set_verbosity() for this purpose.
Higher number means more logging. 

> Choices are [0,2].
> Default is 0. Default will captures WARNING, ERROR, and CRITICAL logs.
> Provide 1 to also capture INFO logs. 
> Provide 2 to also capture DEBUG logs.

    # Enable maximum logging for your python package
    my_package_name = __name__.split('.')[0]
    uologging.set_verbosity(2, args.verbosity_flag, my_package_name)

    # Enable maximum logging for ALL python packages/modules
    uologging.set_verbosity(2)

### argparse 'verbosity flag'

For CLI tools, we provide an integration with argparse to set the logging verbosity.
This integration enables the tool's user to add `-vv` at the command-line for maximum logging verbosity.

> `-v` will enable INFO messages, but not DEBUG.

The verbosity_flag can be gathered via argparse using "`add_verbosity_flag(parser)`":

    import uologging
    import argparse

    parser = argparse.ArgumentParser()
    uologging.add_verbosity_flag(parser)

    args = parser.parse_args(['-vv'])
    # args.verbosity_flag == 2

Now, simply call "`set_verbosity()`" with `args.verbosity_flag` for your package:

    my_package_name = __name__.split('.')[0]
    uologging.set_verbosity(args.verbosity_flag, my_package_name)


## Example: Configuring CLI tool with console & syslog logging

Let's imagine you have a package "`examplepkg`" with a CLI tool in the "`mytool`" module.

    # my_cli_tool.py
    import argparse
    import uologging

    # Parse CLI arguments, '-vv' will result in maximum logging verbosity.
    parser = argparse.ArgumentParser()
    uologging.add_verbosity_flag(parser)
    args = parser.parse_args()

    # Initialize logging
    my_package_name = __name__.split('.')[0]
    uologging.init_console(my_package_name)
    uologging.init_syslog(my_package_name)
    uologging.set_verbosity(args.verbosity_flag, my_package_name)

## Logging messages format

The formatting for log messages can be set via the `log_format` parameter of the `init_console()` and `init_syslog()` functions.

Here are a couple of lines showing what you can expect your logs to looks like by default (`VERBOSE` format):

    2022-01-07 15:40:09 DEBUG    Some simle message for you [hello.py:10]
    2022-01-07 15:40:09 DEBUG    Finished: example.hello:hello((),{}) [hello.py:10] 
    2022-01-07 15:40:09 DEBUG    example.hello:hello((),{}) execution time: 0.00 sec [hello.py:10] 

There are some predefined formats you can use from `uologging.format`:
* `TERSE` - Only the message is logged.
* `TIMESTAMP` - Adds iso-datetime, severity/level
* `VERBOSE` (*default*) - Adds source file/line (along with everything in `TIMESTAMP`)

Override the default format by providing the `log_format` parameter to `init_console()` or `init_syslog()`:

    uologging.init_console(my_package_name, log_format=uologging.format.TERSE)

## Tracing a function

There is a simple `trace` decorator you can use in your python modules to log the 'execution time' of any of your functions.

> The trace decorator logs at DEBUG level by default.
> So, call `set_verbosity(>=2)` to see the trace messages in your logs.

    # hello.py
    import logging
    import uologging

    logger = logging.getLogger(__name__)

    @uologging.trace(logger)
    def hello():
        print('hello!')
    
    hello()

Expect the following messages to be logged:

    2022-01-07 15:40:09 DEBUG    Starting: example.hello:hello((),{}) [hello.py:10]
    hello!
    2022-01-07 15:40:09 DEBUG    Finished: example.hello:hello((),{}) [hello.py:10] 
    2022-01-07 15:40:09 DEBUG    example.hello:hello((),{}) execution time: 0.00 sec [hello.py:10]

## Tracing Concurrent Downloads

Assume you have some service, and you need to make *several http requests* to download *lots of gobs of data*.
You want to do it concurrently, to save on time.

> ℹ 'Downloading data via several http requests' is an example of an '*embarrassingly parallel*' problem. 
> I.e. for each concurrent worker we add, we gain 1x speedup Lots of speedup. 
> Ex. using *8 workers will give 8x speedup.*

For this big, concurrent download, you would like to see:
1. *download progress indications*, to know that the download is indeed happening, and
2. when the download is completed, *how much in total was downloaded.*

There is the `uologging.DownloadTracer` for that!

> The download tracer logs a message for every 1 MB downloaded by default (customizable via '`threshold_bytes`').

Trace a concurrent downloads using the `DownloadTracer` with [python `requests` package](https://pypi.org/project/requests/) like the following:

```python
from concurrent.futures import ThreadPoolExecutor
import requests
import uologging

download_tracer = DownloadTracer('MyService', threshold_bytes=750000)
ALL_MY_URLS = ['http://ex1.io', 'http://ex2.io', 'http://ex3.io']  # ... Replace with your actual list of URLs

def http_get(url):
    respons = requests.get(url)
    download_tracer.trace(len(response.content))
    return response

with ThreadPoolExecutor(max_workers=4) as executor:
    map(http_get, ALL_MY_URLS)
```

## `logging` Best Practices

Use the Python logging package per the following best practices:

1. `logger = logging.getLogger(__name__)` to get the logger for each module/script.
2. Then, use `logger.debug()`, `logger.info()`, `logger.warning()`, etc to add tracing to your Python modules/scripts.

### Example

A trivial example demonstrating best practices:

    # hello.py
    import logging

    logger = logging.getLogger(__name__)

    def hello():
        logger.debug('About to say "hello!"')
        print('hello!')
        logger.debug('Said "hello!"')
