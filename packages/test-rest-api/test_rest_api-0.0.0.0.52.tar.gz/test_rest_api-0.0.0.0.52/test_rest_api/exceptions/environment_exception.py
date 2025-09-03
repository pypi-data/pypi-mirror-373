from ..reporting.report import ErrorType
from .base_exception import TestRestApiException


class EnvironmentException(TestRestApiException):
    """ Custom Exception for Environment """

    def __init__(self, msg):
        super().__init__(msg=msg)
        # Set the error type as 'Environment' which will be used in @test decorator for logging
        self.error = ErrorType.ENVIRONMENT
