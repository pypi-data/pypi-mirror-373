import os
import sys
from dotenv import dotenv_values
from ..runtime.runtime import Runtime
from ..reporting.report import report
from ..utils.error_msg import ErrorMsg
from ..exceptions.decorators import catch_exc
from ..exceptions.environment_exception import EnvironmentException
from ..loggers.test_rest_api_console_logger import test_rest_api_console_logger


class Environment(Runtime):
    """ Environment can be used for parameterization in rest api creation """

    # Override Parent class Runtime -> Meta class to set data_type as 'Immutable'
    class Meta:
        data_type: str = 'Immutable'

    @catch_exc(test_rest_api_exception=EnvironmentException)
    def __getattribute__(self, attribute: str) -> any:
        """ Override __getattribute__ to get the attribute value """
        return super(Environment, self).__getattribute__(attribute)

    @catch_exc(test_rest_api_exception=EnvironmentException)
    def __setattr__(self, attr_name: str, attr_value: any):
        """ Override __setattr__ to set the attribute value """
        # Environment values are immutable, hence cannot be initialised or changed at runtime
        raise Exception(ErrorMsg.ENVIRONMENT_RUNTIME_SET)

    def _set(self, *, path: str) -> None:
        """ Set environment from file path. Supported file extensions: env """
        # Set environment from .env file
        self._set_from_env_file(path=path)

    def _set_from_env_file(self, *, path: str) -> None:
        """ Set environment variables from .env file """
        # Return if path is empty or None
        if not path:
            return
        # Logging to console
        test_rest_api_console_logger.info('Configuring environment from .env file')
        try:
            # Get env file
            env = dotenv_values(path)
            # Initialise count for saving the number of environment values initialised
            count: int = 0
            # Create environment variables from env file key & values
            for name, value in env.items():
                # Check if value is not empty before setting environment
                if value:
                    # Set environment
                    self._set_attr(attr_name=name, attr_value=value)
                    # Increment count
                    count += 1
        except Exception as exc:
            sys.exit(f'{exc}\nFile : {os.path.basename(path)}\nPath : {path}')
        # Update report summary with environment variables count
        report.summary.test.environment_variables = count
        # Logging to console
        test_rest_api_console_logger.info(f'Initialised {count} environment values from .env file')

    def _set_attr(self, *, attr_name: str, attr_value: any) -> None:
        """ Set the Environment instance attribute """
        # Check for duplicates
        self._check_for_duplicates(attr_name=attr_name, attr_value=attr_value)
        # Environment instance attribute
        # Call the base version of __setattr__ you avoid the infinite recursive error
        super(Environment, self).__setattr__(attr_name, attr_value)

    def _check_for_duplicates(self, *, attr_name: str, attr_value: any) -> None:
        """ Check for duplicates in environment file by checking duplicate attribute names """
        # String representation of attr_name & attr_value for exception messages
        input_details = f'\nName : {attr_name}\nValue: {attr_value}'
        # Check for duplicates
        try:
            # Retrieve the value of the attribute
            value = super(Environment, self).__getattribute__(attr_name)
        except Exception as exc:
            value = None
        finally:
            # If the attribute is already set, raise an exception
            if value:
                # Raise exception for duplicate environment variables
                raise Exception(f'{ErrorMsg.ENVIRONMENT_DUPLICATE}{input_details}')


environment: Environment = Environment()
