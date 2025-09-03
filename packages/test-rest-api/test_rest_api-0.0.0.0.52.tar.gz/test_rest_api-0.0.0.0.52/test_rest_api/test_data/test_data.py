import os
import sys
import json
from ..runtime.runtime import Runtime
from ..reporting.report import report
from ..utils.error_msg import ErrorMsg
from ..exceptions.decorators import catch_exc
from ..loggers.test_rest_api_console_logger import test_rest_api_console_logger
from ..exceptions.testdata_exception import TestDataException


class TestData(Runtime):
    """
    Test data can be used for parameterization in tests
    """

    class Meta:
        data_type: str = 'Immutable'

    @catch_exc(test_rest_api_exception=TestDataException)
    def __getattribute__(self, attribute: str) -> any:
        return super(TestData, self).__getattribute__(attribute)

    @catch_exc(test_rest_api_exception=TestDataException)
    def __setattr__(self, attr_name: str, attr_value: any) -> None:
        raise Exception(ErrorMsg.TEST_DATA_RUNTIME_SET)

    def _set(self, *, path: str) -> None:
        """
        Set test data from file/folder path. Supported file extensions: [json, ]
        """
        # Return if test data path list is empty
        if not path:
            return
        # Logging
        test_rest_api_console_logger.info('Auto detecting test data files')
        # Set test data from json files
        self._set_from_json_files(path=path)

    def _set_from_json_files(self, *, path: str) -> None:
        """
        Set test data from json files
        """
        # Initialise json_file_paths list to store all the auto fetched json file paths
        self.__dict__['json_file_paths'] = []
        # Auto detect json file paths
        self._get_json_file_paths(path=path)
        # Return if test data json file path list is empty
        if not self.json_file_paths:
            return
        # Logging
        test_rest_api_console_logger.info(f'Configuring test data from json files')
        try:
            # Total test data count
            test_data_count = 0
            # Iterate through each json file path
            for file in self.json_file_paths:
                # Open json file
                with open(file, encoding="utf-8", ) as f:
                    # Load Json data
                    data = json.load(f)
                    # Count the total keys in this file & update the total count
                    test_data_count += len(data)
                    # Iterating through the json data
                    for name, value in data.items():
                        # Set test data attribute
                        self._set_attr(attr_name=name, attr_value=value)
        except Exception as exc:
            sys.exit(f'{exc}\nFile : {os.path.basename(file)}\nPath : {file}')
        # Total test data count
        test_file_count: int = len(self.json_file_paths)
        # Update report summary with testdata variables count
        report.summary.test.testdata_variables = test_data_count
        report.summary.test.testdata_files = test_file_count
        # Logging
        test_rest_api_console_logger.info(
            f'Initialised {test_data_count} test data variables from {test_file_count} json files')

    def _get_json_file_paths(self, *, path: str) -> None:
        """
        Auto-detect json files from a test data folder/file path to a list
        Files can be under any nested folder
        """
        if path.endswith("__pycache__") or path.endswith('.py'):
            return
        if os.path.isfile(path) and path.endswith('.json'):
            self.json_file_paths.append(path)
        elif os.path.isdir(path):
            for nested_path in os.listdir(path):
                self._get_json_file_paths(path=path + "/" + nested_path)

    def _set_attr(self, *, attr_name: str, attr_value: any) -> None:
        """
        Set the class attribute
        """
        # String representation of name & value for exception messages
        input_details = f'\nKey  : {attr_name}\nValue: {attr_value}'
        # Check if name is of type string
        if not isinstance(attr_name, str):
            raise Exception(f'{ErrorMsg.TEST_DATA_INVALID_DATA_TYPE}{input_details}')
        # Check if name not empty
        if attr_name.strip() == '':
            raise Exception(f'{ErrorMsg.TEST_DATA_EMPTY_STRING}{input_details}')
        # Check for duplicates
        try:
            value = super(TestData, self).__getattribute__(attr_name)
        except Exception as exc:
            value = None
        finally:
            if value:
                raise Exception(f'{ErrorMsg.TEST_DATA_DUPLICATE}{input_details}')
        # Set class level attribute
        # Call the base version of __setattr__ you avoid the infinite recursive error
        super(TestData, self).__setattr__(attr_name, attr_value)


testdata = TestData()
