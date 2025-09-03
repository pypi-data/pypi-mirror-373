from .. import settings
from ..reporting import report
from ..traceback_formatter.test_rest_api_exc_traceback_formatter import TestRestApiExcTracebackFormatter


class TestRestApiException(Exception):
    """ Base Exception class """

    def _format(self) -> None:
        """ Convert the message to Html reporting format """
        _no_data_to_display: str = 'No data to display'
        self.msg = f"""
<b>EXCEPTION</b>
^^^^^^^^^
{settings.logging.sub_point} Message {settings.logging.key_val_sep} {self.msg.strip() if self.msg.strip() else _no_data_to_display}
"""

    def __init__(self, *, msg: str, original: Exception | None = None):
        self.msg: str = msg
        # Save the original exception. This helps debug faster with actual root cause
        self.original = original
        # Convert the msg to reporting format
        self._format()
        # Set the test status to 'ERROR' which will be used in @test decorator for logging
        self.test_status: str = report.TestStatus.ERROR
        # Set the formatter as TestRestApiExcTracebackFormatter which will be used in @test decorator for logging
        self.formatter: TestRestApiExcTracebackFormatter = TestRestApiExcTracebackFormatter()
        # Call Exception __init__ method
        super().__init__(self.msg)
