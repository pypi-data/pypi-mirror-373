from ..reporting.report import ErrorType
from .base_exception import TestRestApiException


class VariableException(TestRestApiException):
    """ Custom Exception for Variable """

    def __init__(self, msg):
        super().__init__(msg=msg)
        # Set the error type as 'Variable' which will be used in @test decorator for logging
        self.error = ErrorType.VARIABLE
