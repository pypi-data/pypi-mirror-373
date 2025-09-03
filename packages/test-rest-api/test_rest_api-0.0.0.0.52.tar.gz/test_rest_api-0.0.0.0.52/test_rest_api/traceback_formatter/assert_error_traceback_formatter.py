import re
from .base_traceback_formatter import TracebackFormatter


class AssertErrorTracebackFormatter(TracebackFormatter):
    def format(self, traceback: str) -> str:
        re_search_end = r'\nAssertionError'
        start_res = re.search(self.re_search_start, traceback)
        traceback = traceback[start_res.end():]
        end_res = re.search(re_search_end, traceback)
        traceback = traceback[:end_res.start()]
        if 'assert False, exc.args[0]' in traceback:
            traceback = traceback[:traceback.rfind('File "') - 3]
        return f'{self.header}{traceback}'
