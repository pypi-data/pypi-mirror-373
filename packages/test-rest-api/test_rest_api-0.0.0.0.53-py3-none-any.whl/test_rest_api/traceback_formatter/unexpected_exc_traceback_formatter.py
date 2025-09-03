import re
from .base_traceback_formatter import TracebackFormatter


class UnexpectedExcTracebackFormatter(TracebackFormatter):
    def format(self, traceback: str) -> str:
        start_res = re.search(self.re_search_start, traceback)
        traceback = traceback[start_res.end():]
        return f'{self.header}{traceback}'
