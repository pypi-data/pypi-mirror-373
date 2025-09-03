import logging
from typing import override
from ..reporting.report import report, ReportTestResultLog


class TestRestApiReportHandler(logging.Handler):
    """
    Custom handler class to add log record message to test rest api report
    This class inherits logging.Handler class and will help to add log record message directly to test rest api report
    """

    @override
    def emit(self, record):
        """ Override emit method of logging.Handler class to add log record message to test rest api report """
        # Get the test case name from log record using taskName attribute
        testcase_name = record.taskName
        # Get ReportTestResultLog instance by formatting record
        log: ReportTestResultLog = self.format(record)
        # Add log record to the test case logs
        report._add_to_testcase_logs(testcase_name=testcase_name, log=log)
        # Update the test report with test result counts based on the log record
        if (test_result_counts_item := getattr(record, '_increment_test_result_counts', None)) is not None:
            report._increment_test_result_counts(testcase_name=testcase_name,
                                                 test_result_counts_item=test_result_counts_item)
