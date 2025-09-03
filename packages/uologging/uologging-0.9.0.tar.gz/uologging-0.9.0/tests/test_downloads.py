from concurrent.futures import ThreadPoolExecutor

import pytest
from assertpy import assert_that
from uologging.downloads import DownloadTracer

log_message_count = 0
@pytest.mark.parametrize('request_count,request_bytes,threshold_bytes,expected_msg_count', [
    (1, 1, 0, 1),  # threshold_bytes=0 means log every request
    (1, 100, 1001, 0),
    (10, 100, 999, 1),
    (100, 100, 999, 10),
])
def test_download_tracer(request_count, request_bytes, threshold_bytes, expected_msg_count, caplog):
    # Arrange
    # A 'spy' function, to see what gets logged
    global log_message_count
    log_message_count = 0
    def spy_log_function(msg):
        global log_message_count
        log_message_count += 1
    download_tracer = DownloadTracer('MyService', threshold_bytes=threshold_bytes, log_function=spy_log_function)
    # Our custom 'http_get' function
    def http_get(url):
        download_tracer.trace(request_bytes)
    # A list of fake URLs to 'download'
    urls = [f'http://fake-url/{num}' for num in range(0, request_count)]

    # Act
    # Use ThreadPoolExecutor to concurrently download the URLs
    with ThreadPoolExecutor(max_workers=10) as executor:
        responses = executor.map(http_get, urls)

    # Assert
    assert_that(download_tracer.total_bytes).is_equal_to(request_count * request_bytes)
    assert_that(log_message_count).is_equal_to(expected_msg_count)

    # Cleanup
    log_message_count = 0
