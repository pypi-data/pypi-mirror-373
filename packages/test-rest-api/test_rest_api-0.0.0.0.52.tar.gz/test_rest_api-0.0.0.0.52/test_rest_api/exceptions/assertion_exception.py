from ..reporting.report import ErrorType
from .base_exception import TestRestApiException
from ..traceback_formatter.assert_exc_traceback_formatter import AssertExcTracebackFormatter


class AssertException(TestRestApiException):
    """ Custom Exception for Assertion """

    def __init__(self, msg):
        super().__init__(msg=msg)
        # Set the error type as 'Assertion' which will be used in @test decorator for logging
        self.error: str = ErrorType.ASSERTION
        # Set the formatter as AssertExcTracebackFormatter which will be used in @test decorator for logging
        self.formatter: AssertExcTracebackFormatter = AssertExcTracebackFormatter()
