from ..reporting.report import ErrorType
from .base_exception import TestRestApiException


class ConstantException(TestRestApiException):
    """ Custom Exception for Constant """

    def __init__(self, msg):
        super().__init__(msg=msg)
        # Set the error type as 'Constant' which will be used in @test decorator for logging
        self.error = ErrorType.CONSTANT
