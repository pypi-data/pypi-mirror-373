import re
from .base_traceback_formatter import TracebackFormatter


class TestRestApiExcTracebackFormatter(TracebackFormatter):
    def format(self, traceback: str) -> str:
        re_search_end = r'raise test_rest_api_exception'
        start_res = re.search(self.re_search_start, traceback)
        end_res = re.search(re_search_end, traceback)
        traceback = traceback[start_res.end():end_res.end()]
        traceback = traceback[:traceback.rfind('File "') - 3]
        return f'{self.header}{traceback}'
