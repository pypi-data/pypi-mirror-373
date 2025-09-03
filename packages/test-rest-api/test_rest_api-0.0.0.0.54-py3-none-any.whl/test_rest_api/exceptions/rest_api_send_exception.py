from ..reporting.report import ErrorType
from .base_exception import TestRestApiException


class RestApiSendException(TestRestApiException):
    """ Custom Exception for Rest API Send """

    def __init__(self, msg, original: Exception | None = None):
        super().__init__(msg=msg, original=original)
        # Set the error type as 'Rest API' which will be used in @test decorator for logging
        self.error = ErrorType.REST_API
