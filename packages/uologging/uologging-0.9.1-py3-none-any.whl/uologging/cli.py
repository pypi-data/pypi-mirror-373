import argparse


def add_verbosity_flag(parser: argparse.ArgumentParser):
    """Add a --verbose/-v flag to an argparse.ArgumentParser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to be updated.

    Example:
        This should be invoked like the following:
        >>> import uologging
        >>> import argparse
        >>> parser = argparse.ArgumentParser()
        >>> uologging.add_verbosity_flag(parser)

        When parsing args, the verbosity_flag will be set if --verbose/-v is passed!
        >>> args = parser.parse_args(['-vv'])
        >>> args.verbosity_flag
        2

        The verbosity_flag is intended to be used as input for uologging.set_logging_verbosity().
    """
    parser.add_argument(
        '-v', '--verbose',
        dest='verbosity_flag',
        action='count',
        default=0,
        help='Logging verbosity. "-vv" results in maximum logging.'
    )


def get_default_parser():
    """Provides an argparse ArgumentParser configured to take --verbose/-v flag.

    Returns:
        argparse.ArgumentParser: Provides a --verbose/-v flag. Should be used as a 'parent parser.'

    Example:
        This should be invoked like the following:
        >>> import uologging
        >>> import argparse
        >>> parser = argparse.ArgumentParser(parents=[uologging.get_default_parser()])

        The parser has been configured with the uologging default_parser as a parent parser.
        When parsing args, the verbosity_flag will be set if --verbose/-v is passed!
        >>> args = parser.parse_args(['-vv'])
        >>> args.verbosity_flag
        2

        The verbosity_flag is intended to be used as input for uologging.set_logging_verbosity().
    """
    parser = argparse.ArgumentParser(add_help=False)
    add_verbosity_flag(parser)
    return parser
