import logging
from typing import override


class TestRestApiConsoleFilter(logging.Filter):
    """ Custom filter to log records to test rest api console logger """

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """ Override filter method """
        # Only log records from test_rest_api_console logger to console for this particular handler
        # This filter will be used in test_rest_api_console_handler
        # This will not restrict other third party loggers to log records to console
        return record.name == "test_rest_api_console"


class TestRestApiReportFilter(logging.Filter):
    """ Custom filter to log records to test rest api report logger """

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """ Override filter method """
        # Only log records from test_rest_api_report logger to report for this particular handler
        return record.name == "test_rest_api_report"
