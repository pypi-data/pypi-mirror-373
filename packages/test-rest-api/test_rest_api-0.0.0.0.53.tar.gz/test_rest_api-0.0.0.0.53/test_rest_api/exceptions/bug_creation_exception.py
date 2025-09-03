from ..reporting import report
from .base_exception import TestRestApiException


class BugCreationException(TestRestApiException):
    """ Custom Exception for Bug Creation """

    def __init__(self, msg):
        super().__init__(msg=msg)
        # Set the error type as 'Bug' which will be used in @test decorator for logging
        self.error = report.ErrorType.BUG
