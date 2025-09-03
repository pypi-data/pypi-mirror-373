import os
import sys
import json
import types
import logging
import aiohttp
import asyncio
import inspect
import traceback
import importlib.machinery
from datetime import datetime
from inspect import getmembers
from time import perf_counter_ns
from asyncio import iscoroutinefunction, Task
from typing import override, TypeVar, Callable, Awaitable
from ..reporting.report import report
from ..utils.error_msg import ErrorMsg
from ..test_data.test_data import testdata
from ..environment.environment import environment
from ..utils.aiohttp_session import AioHttpSession
from ..loggers.test_rest_api_console_logger import test_rest_api_console_logger

T = TypeVar("T")
AsyncFunc = Callable[[], Awaitable[T]]


class BaseRunnerMeta(type):
    """ Metaclass for BaseRunner """

    @override
    def __new__(cls, name, bases, attrs):
        """ Executed only once when the class is created """
        # Only execute for Runer Base Class
        if not bases:
            # Initialise the set of validation method names to empty set
            validation_method_names: set = set()
            # Loop through all the attributes of the class and get the method names starting with '_validate_'
            for method_name in [attr for attr in attrs if attr.startswith("_validate_")]:
                # Add the method name to the set. Set will take care of duplications
                validation_method_names.add(method_name)
            # Add the set of validation method names to the class attributes
            attrs['_validation_method_names'] = validation_method_names
        # Return the class object
        return super(BaseRunnerMeta, cls).__new__(cls, name, bases, attrs)

    @override
    def __call__(cls, *args, **kwargs):
        """ Executed when an instance of the class is created """
        # Create an object to be returned
        obj = super(BaseRunnerMeta, cls).__call__(*args, **kwargs)
        # Loop through all the validation method names and execute them
        for method_name in obj._validation_method_names:
            # Get the object method from the object
            if (obj_method := getattr(obj, method_name, None)):
                # Execute the object method to validate the input instance variables
                obj_method()
        # Package branding in console
        cls._console_branding()
        # Return the object
        return obj

    @staticmethod
    def _console_branding() -> None:
        """ Package branding in Console """
        # Brand name and line item
        brand_name, line_item = 'T E S T - R E S T - A P I', '✧'
        # Full line and half line creation
        full_line, half_line = line_item * 50, line_item * 10
        # Log the branding in console
        for _ in range(2):
            test_rest_api_console_logger.info(full_line)
        test_rest_api_console_logger.info(f'{half_line}  {brand_name}  {half_line}✧')
        for _ in range(2):
            test_rest_api_console_logger.info(full_line)


class BaseRunner(metaclass=BaseRunnerMeta):
    """ Base class for Runner """

    def __init__(self,
                 test_suite_path: str,
                 concurrency: int | str,
                 test_result_path: str | None = None,
                 test_env_path: str | None = None,
                 test_data_path: str | None = None,
                 test_tags: str | None = None):
        # Initialise test suite path
        self.test_suite_path: str = test_suite_path
        # Initialise concurrency
        self.concurrency: int | str = concurrency
        # Test result path is optional and by default its test suite path
        self.test_result_path: str = test_result_path if test_result_path else test_suite_path
        # Initialise test env path
        self.test_env_path: str = test_env_path
        # Initialise test data path
        self.test_data_path: str = test_data_path
        # Initialise test tags
        self.test_tags: list = self._process_test_tags(test_tags=test_tags)

    def _validate_test_suite_path(self):
        """ Validate test suite path """
        conditions = (self.test_suite_path, os.path.exists(self.test_suite_path))
        if all(conditions):
            return
        sys.exit(ErrorMsg.INVALID_TEST_SUITE_PATH)

    def _validate_concurrency(self):
        """ Validate concurrency """
        if not self.concurrency:
            sys.exit(ErrorMsg.INVALID_CONCURRENCY)

        if isinstance(self.concurrency, str):
            if not self.concurrency.isdigit():
                sys.exit(ErrorMsg.INVALID_CONCURRENCY)
            self.concurrency = int(self.concurrency)

        if not isinstance(self.concurrency, int):
            sys.exit(ErrorMsg.INVALID_CONCURRENCY)

    def _validate_test_result_path(self):
        """ Validate test result path """
        if os.path.exists(self.test_result_path):
            return
        sys.exit(ErrorMsg.INVALID_TEST_RESULT_PATH)

    def _validate_test_env_path(self):
        """ Validate test env path """
        # Env path is optional
        if self.test_env_path is None or self.test_env_path.strip() == "":
            return
        if os.path.exists(self.test_env_path):
            return
        sys.exit(ErrorMsg.INVALID_ENV_PATH)

    def _validate_test_data_path(self):
        """ Validate test data path """
        # Test data path is optional
        if self.test_data_path is None or self.test_data_path.strip() == "":
            return
        if os.path.exists(self.test_data_path):
            return
        sys.exit(ErrorMsg.INVALID_TEST_DATA_PATH)

    def _validate_test_tags(self):
        """ Validate test tags """
        if isinstance(self.test_tags, list):
            return
        sys.exit(ErrorMsg.INVALID_TEST_TAG)

    @staticmethod
    def _load_module(*, name: str, path: str):
        """
        Load the module in runtime and return it
        """
        loader = importlib.machinery.SourceFileLoader(name, path)
        module = types.ModuleType(name)
        loader.exec_module(module)
        return module

    @staticmethod
    def _load_sync_tests(*, module):
        """
        From test file load all the @test decorated async function objects with is_async_testcase as False in a list
        Conditions: Is Async Function & Decorated with @test & is_async_testcase is False
        """
        return [obj for _, obj in getmembers(module) if
                inspect.isfunction(obj) and
                inspect.iscoroutinefunction(obj) and
                obj.__dict__.get('is_testcase', False) and not obj.__dict__.get('is_async_testcase', False)]

    @staticmethod
    def _load_async_tests(*, module):
        """
        From test file load all the @test decorated async function objects with is_async_testcase as True in a list
        Conditions: Is Async Function & Decorated with @test & is_async_testcase is True
        """
        return [obj for _, obj in getmembers(module) if
                inspect.isfunction(obj) and
                iscoroutinefunction(obj) and
                obj.__dict__.get('is_testcase', False) and obj.__dict__.get('is_async_testcase', False)]

    @staticmethod
    def _process_test_tags(*, test_tags: str) -> list:
        """ Convert the tags string with #tags to list separated by # """
        # Convert the test tags string with #tags to list separated by #
        test_tags_list: list = test_tags.split("#") if isinstance(test_tags, str) and test_tags.startswith('#') else []
        # Strip all tags and also remove empty tags
        test_tags_list_stripped: list = [test_tag.strip() for test_tag in test_tags_list if test_tag.strip()]
        # Return the list of test tags
        return test_tags_list_stripped


class Runner(BaseRunner):
    """
    Execute all test cases
    Auto detect test suites and test cases
    """

    def __init__(self,
                 test_suite_path,
                 concurrency: int | str,
                 test_result_path=None,
                 env_path=None,
                 test_data_path=None,
                 test_tags=[]):
        # Initialise Base Class
        super(Runner, self).__init__(test_suite_path,
                                     concurrency,
                                     test_result_path, env_path, test_data_path,
                                     test_tags)
        # List of test file paths
        self.test_files: list = []
        # List of test data file paths
        self.test_data_files: list = []
        # List of @test decorated sync function objects
        self.sync_tests: list = []
        # List of @test decorated async function objects
        self.async_tests: list = []
        # Assign the report object to an instance variable
        self.report = report
        # Update the report with the test tags
        self.report.summary.test.tags = tuple(self.test_tags)

    def _load_test_files(self, path):
        """
        Auto-detect python files from a test suite folder/file path to a list
        Files can be under any nested folder
        """
        if path.endswith("__pycache__") or path.endswith(".json"):
            return
        if os.path.isfile(path) and path.endswith('.py'):
            self.test_files.append(path)
        elif os.path.isdir(path):
            for nested_path in os.listdir(path):
                self._load_test_files(path + "/" + nested_path)

    def _load_tests(self):
        """
        Auto-detect @test decorated sync and async functions from the list of test python files
        Update the function objects in tests list
        """
        # Logging
        test_rest_api_console_logger.info(f'Total python files in test suite: {len(self.test_files)}')
        test_rest_api_console_logger.info('Auto detecting tests from python files in test suite')
        # Create a generator of python files from testsuite folder
        test_file_generator = (test_file for test_file in self.test_files)
        # For each file path in list of python files from testsuite folder
        for test_file in test_file_generator:
            # Get file name with extension
            name_with_ext = os.path.basename(self.test_suite_path)
            # Get file name without extension
            name = os.path.splitext(name_with_ext)[0]
            # Load the module in runtime from file paths
            module = Runner._load_module(name=name, path=test_file)
            # Load the @test decorated sync functions as a list from the module
            sync_tests = Runner._load_sync_tests(module=module)
            # Update the sync_tests instance variable
            self.sync_tests.extend(sync_tests)
            # Load the @test decorated async functions as a list from the module
            async_tests = Runner._load_async_tests(module=module)
            # Update the async_tests instance variable
            self.async_tests.extend(async_tests)
            # Log the test file details, only if it has @test decorated functions
            # This avoids logging not testsuite files like util & helper files with zero Async and Sync tests count
            if async_tests or sync_tests:
                # Logging
                test_rest_api_console_logger.info(
                    f'Auto detected {len(async_tests) + len(sync_tests)} ({len(async_tests)} Async & {len(sync_tests)} Sync) tests from testsuite: {test_file}')
        # Logging
        test_rest_api_console_logger.info('Successfully competed auto detection of tests from test suites')
        test_rest_api_console_logger.info(f'Total synchronous tests: {len(self.sync_tests)}')
        test_rest_api_console_logger.info(f'Total asynchronous tests: {len(self.async_tests)}')
        test_rest_api_console_logger.info(f'Total tests: {len(self.sync_tests) + len(self.async_tests)}')
        # Terminate execution if the total testcases count is 0
        if len(self.sync_tests) + len(self.async_tests) == 0:
            sys.exit(ErrorMsg.EMPTY_TESTS)
        # Sort the synchronous tests
        self.sync_tests.sort(key=lambda x: x.execution_order)

    def _setup_testsuite(self):
        """ Set up the test suite """
        # Logging
        test_rest_api_console_logger.info('Started test setup')
        # Load the python files from the test suite path
        self._load_test_files(self.test_suite_path)
        # Load @test decorated functions from the loaded python files
        self._load_tests()
        # Set environment variables from .env file
        environment._set(path=self.test_env_path)
        # Set test data from file/folder path. Supported file extensions: [json, ]
        testdata._set(path=self.test_data_path)
        # Logging
        test_rest_api_console_logger.info('Completed test setup')

    async def _run_tests_sync(self):
        """ Run the synchronous tests """
        # Logging
        test_rest_api_console_logger.info('Started synchronous test execution (Concurrency: 1)')
        # Create a generator of sync tests
        sync_test_generator = (sync_test for sync_test in self.sync_tests)
        # Run each test synchronously
        for sync_test in sync_test_generator:
            # Tasks are created using asyncio.create_task() instead of directly calling the function
            # This is to avoid the same name( asyncio.current_task().get_name() ) for all the sync tasks
            task: Task = asyncio.create_task(sync_test())
            # Await the task to run the test
            await task
        # Logging
        test_rest_api_console_logger.info('Completed synchronous test execution')

    async def _run_tests_async(self):
        """ Run the asynchronous tests """
        # Logging
        test_rest_api_console_logger.info(f'Started asynchronous test execution (Concurrency: {self.concurrency})')

        semaphore = asyncio.Semaphore(self.concurrency)

        async def semaphore_task(func: AsyncFunc):
            async with semaphore:
                try:
                    await func()
                except:
                    pass

        semaphore_tasks: list = [semaphore_task(async_test) for async_test in self.async_tests]

        for future in asyncio.as_completed(semaphore_tasks):
            await future  # discard result

        # Logging
        test_rest_api_console_logger.info('Completed asynchronous test execution')

    async def _run_tests(self):
        """ Run the tests """
        # Run synchronous tests before asynchronous tests
        await self._run_tests_sync()
        # Run asynchronous tests (Execute async functions concurrently)
        await self._run_tests_async()

    @staticmethod
    def _is_logging_completed():
        """ Check if the root logger queue handler has finished processing all the logs """
        # Get the queue handler
        queue_handler = logging.getHandlerByName("queue_handler")
        # Check if queue handler exists
        if queue_handler is None:
            return True
        # Check the queue handler unfinished tasks
        return queue_handler.queue.unfinished_tasks == 0

    def _save_report(self):
        """ Save the test report """
        # Wait until all the log records are processed by the queue handler
        while True:
            if self._is_logging_completed():
                break
        # Create and save the test report
        self.report._save(path=self.test_result_path)
        # Logging summary result in console
        test_rest_api_console_logger.info(self.report.summary)

    async def _run_testsuite(self):
        """ Run the test suite """
        # Set up the testsuite before run
        self._setup_testsuite()
        # Session should be created inside async function even if it itself not an async function
        # Also creation should happen inside the main event loop (Should not be in a separate event loop)
        session = aiohttp.ClientSession(json_serialize=json.dumps)
        # Create an aiohttp session for the whole test run instead of creating a new session per request.
        AioHttpSession.set(session=session)
        # Start the stopwatch / counter
        timer_start = perf_counter_ns()
        # Update test start (date-time) in report
        self.report.summary.test.start = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        # Run the tests
        await self._run_tests()
        # Update test end (date-time) in report
        self.report.summary.test.end = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        # Stop the stopwatch / counter
        timer_stop = perf_counter_ns()
        # Calculate the time duration of the test in seconds (note: duration is in nanoseconds)
        # Update test duration in report
        self.report.summary.test.duration = f'{round((timer_stop - timer_start) / 1000000000, 3)} seconds'
        # Close the aiohttp session after completing the test
        await AioHttpSession().close()
        # Save the test report
        self._save_report()

    def run(self):
        """
        Method to run the testsuite
        This method can be used by the users to trigger the test in code.
        example:
                from test_rest_api import Runner
                runner = Runner(test_suite_path="<Test Suite Path>")
                runner.run()
        """
        try:
            # Run '_run_testsuite' coroutine in an event loop.
            asyncio.run(self._run_testsuite())
        except Exception as exc:
            sys.exit(f"""
{ErrorMsg.UNKNOWN_EXCEPTION}
Error details: {exc}
{traceback.format_exc()}
""")
