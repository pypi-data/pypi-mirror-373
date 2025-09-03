from ..reporting.report import ErrorType
from .base_exception import TestRestApiException


class TestDataException(TestRestApiException):
    """ Custom Exception for Test Data """

    def __init__(self, msg):
        super().__init__(msg=msg)
        # Set the error type as 'Test Data' which will be used in @test decorator for logging
        self.error = ErrorType.TEST_DATA
