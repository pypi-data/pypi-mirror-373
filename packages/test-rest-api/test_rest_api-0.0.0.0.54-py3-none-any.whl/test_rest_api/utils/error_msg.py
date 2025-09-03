from dataclasses import dataclass


@dataclass(frozen=True)
class Docs:
    commands: str = f"""
--------
Commands
--------
-> Run Test Suite
Syntax : test_rest_api -t "<Path to test suite folder/file>" -c <Concurrency value for parallel execution> -r "<Path to test result folder>" -h "<Hash Tags for tests for filtering>" -e "<Path to test environment file>" -d "<Path to test test data folder/file which contains json files>"
Example: test_rest_api -t "/Users/user/Documents/TestSuite" -c 10 -r "/Users/user/Documents/TestResult" -h "#smoke #sanity" -e "/Users/user/Documents/prod.env" -d "/Users/user/Documents/TestData"
"""


@dataclass(frozen=True)
class ErrorMsg:
    INVALID_TEST_SUITE_PATH: str = f"ERROR! Please provide a valid path for the test suite\n{Docs.commands}"
    INVALID_CONCURRENCY: str = f"ERROR! Please provide a valid positive integer for concurrency\n{Docs.commands}"
    INVALID_ENV_PATH: str = f"ERROR! Please provide a valid path for .env file\n{Docs.commands}"
    INVALID_TEST_DATA_PATH: str = f"ERROR! Please provide a valid path for test data\n{Docs.commands}"
    INVALID_TEST_RESULT_PATH: str = f"ERROR! Please provide a valid path for the test result\n{Docs.commands}"
    INVALID_TEST_TAG: str = f"ERROR! Please provide a valid tag list\n{Docs.commands}"
    EMPTY_TESTS: str = "No Tests Found!"
    INVALID_METHOD: str = "Invalid Request Method. Supported methods: 'get', 'post', 'put', 'patch', 'delete', 'head', 'options'"
    UNKNOWN_EXCEPTION: str = "Sorry Something went wrong"
    INVALID_URL: str = "Invalid ULR. Please provide a valid url in rest api creation"
    CLIENT_CONNECTOR_ERROR: str = "Cannot connect to URL host. Please provide a valid url host in rest api creation"
    INVALID_JSON_RESPONSE: str = "Invalid Response Type. Supports only Json type (application/json)"
    CONSTANT_DUPLICATE: str = "Constant cannot be altered at runtime"
    TEST_DATA_DUPLICATE: str = "ERROR! Test Data Duplication. Please provide unique name for the keys in test data json files"
    TEST_DATA_EMPTY_STRING: str = "ERROR! Empty String. Please provide a valid string for the keys in test data json files"
    TEST_DATA_INVALID_DATA_TYPE: str = "ERROR! Invalid Data Type. Please provide a valid string for the keys in test data json files"
    TEST_DATA_RUNTIME_SET = 'Test Data cannot be initialised or altered at runtime'
    ENVIRONMENT_DUPLICATE: str = "ERROR! Environment Duplication. Please provide unique name for the keys in .env file"
    ENVIRONMENT_EMPTY_STRING: str = "ERROR! Empty String. Please provide a valid string for variable name in .env file"
    ENVIRONMENT_INVALID_DATA_TYPE: str = "ERROR! Invalid Data Type. Please provide a valid string for variable name in .env file"
    ENVIRONMENT_RUNTIME_SET: str = 'Environment cannot be initialised or altered at runtime'
    INVALID_BUG_PRIORITY: str = 'Invalid bug priority value. Supported bug priorities: '
    INVALID_BUG_ATTR_DATA_TYPE: str = 'Invalid data type. Please provide a valid string for '
    AWAIT_KEY_WORD_MISSING: str = '\n\nTip: This may be due to not using await keyword in async Rest api send function calls'
    INVALID_URL_DATA_TYPE: str = 'Invalid data type for url. Please provide a valid string'
    INVALID_PARAM_DATA_TYPE: str = 'Please provide a valid dictionary, with both dictionary key and dictionary value as string type'
    INVALID_BODY_DATA_TYPE: str = 'Invalid data type for body. Please provide a valid dictionary'
    INVALID_METHOD_DATA_TYPE: str = 'Invalid data type for method. Please provide a valid string'
