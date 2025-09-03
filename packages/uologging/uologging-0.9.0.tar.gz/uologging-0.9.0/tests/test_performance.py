
import logging
import time

import pytest
from assertpy import assert_that

import uologging


@pytest.mark.parametrize("log_level", [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])
def test_trace_at_log_level(caplog, log_level):
    # Arrange
    execution_time = 0.1
    with caplog.at_level(log_level):
        uologging.init_console()
        logger = logging.getLogger(__name__)

        @uologging.trace(logger, level=log_level)
        def test_method():
            time.sleep(execution_time)

        # Act
        test_method()

    # Assert - May fail on very slow computers...
    assert_that(caplog.text).contains(f'Starting: {__name__}:{test_method.__name__}')
    assert_that(caplog.text).contains(f'Finished: {__name__}:{test_method.__name__}')
    assert_that(caplog.text).contains(f'exec time: {execution_time}')


def test_trace_dont_capture_secret_arguments(caplog):
    # Arrange
    with caplog.at_level(logging.DEBUG):
        uologging.init_console()
        logger = logging.getLogger(__name__)

        @uologging.trace(logger, capture_args=False)
        def test_method(password):
            pass

        # Act
        test_method('SuperSecretPassword')

    # Assert
    assert_that(caplog.text).does_not_contain('SuperSecretPassword')


def test_trace_capture_arguments(caplog):
    # Arrange
    with caplog.at_level(logging.DEBUG):
        uologging.init_console()
        logger = logging.getLogger(__name__)

        @uologging.trace(logger)
        def test_method(arg, another_arg=None):
            pass

        # Act
        test_method('Bird', 
                    another_arg=['is', 'the', 'word!'])

    # Assert
    assert_that(caplog.text).contains("test_method('Bird', another_arg=['is', 'the', 'word!'])")
