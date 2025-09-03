import re
from .base_traceback_formatter import TracebackFormatter


class BugExcTracebackFormatter(TracebackFormatter):
    def format(self, traceback: str) -> str:
        re_search_end = r'raise Bug'
        start_res = re.search(self.re_search_start, traceback)
        end_res = re.search(re_search_end, traceback)
        traceback = traceback[start_res.end():end_res.end()]
        return f'{self.header}{traceback}'
