class TracebackFormatter:
    def __init__(self):
        self.header = f"""
<b>TRACEBACKS</b>
^^^^^^^^^^
"""
        self.re_search_start = r'test_rest_api[//\\]decorator[//\\]decorator.py", line (.*?), in inner\n    await func\(\*args, \*\*kwargs\)\n'

    def format(self):
        pass
