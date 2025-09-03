from ..reporting.report import ErrorType
from .base_exception import TestRestApiException


class RestApiCreationException(TestRestApiException):
    """ Custom Exception for Rest API Creation """

    def __init__(self, msg):
        super().__init__(msg=msg)
        # Set the error type as 'Rest API' which will be used in @test decorator for
        self.error = ErrorType.REST_API
