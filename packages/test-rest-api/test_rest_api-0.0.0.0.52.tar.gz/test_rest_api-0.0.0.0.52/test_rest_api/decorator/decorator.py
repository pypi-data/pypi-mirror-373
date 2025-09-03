import asyncio
import itertools
import traceback
import functools
from itertools import count
from datetime import datetime
from time import perf_counter_ns
from inspect import iscoroutinefunction
from ..bug.bug import Bug
from .hashtag_filter import skip_test
from ..reporting.report import report
from ..utils.error_msg import ErrorMsg
from ..exceptions.base_exception import TestRestApiException
from ..reporting.report import ReportTestResult, TestStatus, ErrorType
from ..loggers.test_rest_api_report_logger import test_rest_api_report_logger
from ..loggers.test_rest_api_console_logger import test_rest_api_console_logger
from ..traceback_formatter.assert_error_traceback_formatter import AssertErrorTracebackFormatter
from ..traceback_formatter.unexpected_exc_traceback_formatter import UnexpectedExcTracebackFormatter

# Iter for creating id for testcase name
iter_test_name: itertools.count = count(start=1)


def test(*, name: str = '', desc: str = '', enabled: bool = True,
         tags: str = '', is_async: bool = True, execution_order: str = 'z'):
    def testcase_decorator(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            # Get the test file path
            testsuite: str = func.__module__ if func.__module__ else 'root file'
            # Create the test name & also add unique id at the end (Users can provide same name for multiple testcases)
            testcase_name: str = f'{name} ({testsuite}) [{next(iter_test_name)}]' if name else f'{func.__name__} ({testsuite}) [{next(iter_test_name)}]'
            # Create the test description. Capitalize if already provided else provide default No description msg
            testcase_desc: str = desc.capitalize() if desc.strip() else 'No description provided'
            # Set the current task name to testcase name
            asyncio.current_task().set_name(testcase_name)
            # Initialise start and end time of the test
            start = end = 'Test not started'
            # Initialise the bug priority with default value
            bug_priority: str = 'No Bugs Found'
            # Initialise the error type with default value
            error_type: str = 'No Errors Found'
            # Initialise the test duration with default value
            duration: str = '0 seconds'
            # Set Disable details
            status, details = TestStatus.DISABLE, 'Testcase is disabled'
            # Update the test result in the report before the test execution
            report._update_testcase_result_before_testcase_execution(testcase_name=testcase_name,
                                                                     desc=testcase_desc,
                                                                     testsuite=testsuite,
                                                                     is_async=is_async,
                                                                     tags=tags,
                                                                     execution_order=execution_order)
            # Only execute enabled testcases
            if enabled:
                # Set Skip details
                status, details = TestStatus.SKIP, 'Testcase is skipped'
                # Skip the test if execution #tags not present in test #tags
                if not skip_test(tags=tags):
                    try:
                        # Start the stopwatch / counter
                        timer_start = perf_counter_ns()
                        # Get the start date time of the test
                        start = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                        # Log the test execution started in the report
                        test_rest_api_report_logger.info('<b>Testcase execution started</b>', extra={'internal': True})
                        # Call the async test function
                        await func(*args, **kwargs)
                        # Update the test status and details
                        status, details = TestStatus.PASS, '<b>Successfully completed the testcase execution</b>'
                    # Catch all the TestRestApiException child exceptions raised internally by the framework
                    except TestRestApiException as exc:
                        # Get the code traceback details
                        traceback_data = traceback.format_exc()
                        # Format the traceback data to remove unwanted info
                        # Formatter will be dynamic based on the exception type
                        traceback_data_formatted = exc.formatter.format(traceback=traceback_data)
                        # Combine the exception message and traceback data to provide detailed info in the details tab
                        details = f'{exc}{traceback_data_formatted}'
                        # Set the test status
                        # test status will be dynamic based on the exception type
                        status = exc.test_status
                        # Set the error type
                        # error type will be dynamic based on the exception type
                        error_type = exc.error
                    # Cath Bug exception raised by the user in test functions. eg: raise Bug()
                    except Bug as exc:
                        # Get the code traceback details
                        traceback_data = traceback.format_exc()
                        # Format the traceback data to remove unwanted info
                        # Formatter will be dynamic based on the exception type
                        traceback_data_formatted = exc.formatter.format(traceback=traceback_data)
                        # Combine the exception message and traceback data to provide detailed info in the details tab
                        details = f'{exc}{traceback_data_formatted}'
                        # Set the test status
                        # test status will be dynamic based on the exception type
                        status = exc.test_status
                        # Set the bug priority
                        # bug priority will be dynamic based on the exception type
                        bug_priority = exc.priority
                    # Catch AssertionError raised by the user in test functions. eg: assert False
                    except AssertionError as exc:
                        # Get the code traceback details
                        traceback_data = traceback.format_exc()
                        # Format the traceback data to remove unwanted info
                        traceback_data_formatted = AssertErrorTracebackFormatter().format(traceback=traceback_data)
                        # Combine the exception message and traceback data to provide detailed info in the details tab
                        details = f'{exc}{traceback_data_formatted}'
                        # Set the test status to FAIL as it's an assertion error
                        status = TestStatus.FAIL
                        # Set the bug priority
                        bug_priority = exc.args[0].priority if exc.args and isinstance(exc.args[0],
                                                                                       Bug) else Bug.PRIORITY.LOW
                    # Catch all other exceptions raised in test functions
                    except Exception as exc:
                        # Format the exc str to report format
                        test_rest_api_exc = TestRestApiException(msg=str(exc))
                        # Get the code traceback details
                        traceback_data = traceback.format_exc()
                        # Format the traceback data to remove unwanted info
                        traceback_data_formatted = UnexpectedExcTracebackFormatter().format(traceback=traceback_data)
                        # Combine the exception message and traceback data to provide detailed info in the details tab
                        details = f'{test_rest_api_exc.msg}{traceback_data_formatted}'
                        # Set the test status to ERROR as it's an unexpected error
                        status = TestStatus.ERROR
                        # Set the error type to UNEXPECTED as it's an unexpected error
                        error_type = ErrorType.UNEXPECTED
                        # If the error is due to missing await keyword in async function calls
                        # Provide a tip for error caused due to await keyword missing scenarios
                        if "'coroutine' object has no attribute" in test_rest_api_exc.msg:
                            details += ErrorMsg.AWAIT_KEY_WORD_MISSING
                    # Finally block will always execute irrespective of the exception
                    finally:
                        # Set the end time of the test
                        end = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                        # Stop the stopwatch / counter
                        timer_stop = perf_counter_ns()
                        # Calculate the time duration of the test in seconds (note: duration is in nanoseconds)
                        duration = f'{round((timer_stop - timer_start) / 1000000000, 3)} seconds'
                        # Log to report & console loggers
                        # Console logger will always be INFO level as its providing info about the test status
                        # Report logger level will be based on the test status
                        if status == TestStatus.PASS:
                            test_rest_api_report_logger.info(details, extra={'internal': True})
                            test_rest_api_console_logger.info(f"{'🟢PASS' : <9}⏰{duration : <20}📂{testcase_name}")
                        elif status == TestStatus.FAIL:
                            test_rest_api_report_logger.warning(details, extra={'internal': True})
                            test_rest_api_console_logger.info(f"{'🔴FAIL' : <9}⏰{duration : <20}📂{testcase_name}")
                        elif status == TestStatus.ERROR:
                            test_rest_api_report_logger.error(details, extra={'internal': True})
                            test_rest_api_console_logger.info(f"{'🟡ERROR' : <9}⏰{duration : <20}📂{testcase_name}")

            report._update_testcase_result_after_testcase_execution(testcase_name=testcase_name,
                                                                    status=status,
                                                                    details=details,
                                                                    start=start,
                                                                    end=end,
                                                                    duration=duration,
                                                                    bug_priority=bug_priority,
                                                                    error_type=error_type)

        # Only async functions can be decorated with @test
        inner.is_testcase = True if iscoroutinefunction(func) else False
        inner.is_async_testcase = is_async
        # For ordering sequential testcases
        inner.execution_order = execution_order
        return inner

    return testcase_decorator
