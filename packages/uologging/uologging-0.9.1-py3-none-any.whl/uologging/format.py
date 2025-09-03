import logging

VERBOSE = logging.Formatter(
    "%(asctime)s %(levelname)-8s  %(message)s [%(pathname)s:%(lineno)d]",
    "%Y-%m-%d %H:%M:%S",
)

TIMESTAMP = logging.Formatter(
    "%(asctime)s %(levelname)-8s  %(message)s", "%Y-%m-%d %H:%M:%S"
)

TERSE = logging.Formatter("%(message)s")
