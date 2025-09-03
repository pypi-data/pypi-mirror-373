from dataclasses import asdict
from .. import settings
from .method import RestApiMethod
from ..utils.error_msg import ErrorMsg
from ..utils.aiohttp_session import AioHttpSession
from .response import RestApiResponse, ClientResponse
from ..exceptions.decorators import catch_exc, catch_exc_async
from ..exceptions.rest_api_send_exception import RestApiSendException
from ..exceptions.rest_api_creation_exception import RestApiCreationException
from ..loggers.test_rest_api_report_logger import test_rest_api_report_logger


class RestApi:
    """
    Class for creating rest api instances
    """
    # Create a frozen instance of RestApiMethod, so that it can be used as a constant in code
    METHODS = RestApiMethod()

    def _validate(self):
        """ Validate class attributes """
        # Validate url
        self._validate_url()
        # Validate parameters and headers
        self._validate_parameters_and_headers()
        # Validate body
        self._validate_body()

    def _validate_url(self):
        """
        Checks
        ------
        1. Valid string
        """
        if not isinstance(self.url, str):
            raise Exception(ErrorMsg.INVALID_URL_DATA_TYPE)

    def _validate_parameters_and_headers(self):
        """
        Checks
        ------
        1. Valid dictionary
        2. Valid dictionary schema
        """
        error = ErrorMsg.INVALID_PARAM_DATA_TYPE
        for item in ('parameters', 'headers'):
            if not isinstance(getattr(self, item), dict):
                raise Exception(f'Invalid data type for {item}. {error}')
            if not all([isinstance(key, str) and isinstance(key, str) for key, value in
                        getattr(self, item).items()]):
                raise Exception(f'Invalid dictionary for {item}. {error}')

    def _validate_body(self):
        """
        Checks
        ------
        1. Valid dictionary
        """
        if not isinstance(self.body, dict):
            raise Exception(ErrorMsg.INVALID_BODY_DATA_TYPE)

    @catch_exc(test_rest_api_exception=RestApiCreationException)
    def __init__(self, url: str, parameters: dict | None = None, headers: dict | None = None, body: dict | None = None,
                 **kwargs):
        # Rest api variables
        self.url = url
        self.parameters = {} if parameters is None else parameters
        self.headers = {} if headers is None else headers
        self.body = {} if body is None else body
        self.kwargs = kwargs
        # Validate url, parameters, headers and body
        self._validate()
        # Aiohttp session
        self._session = AioHttpSession()
        # Logging
        test_rest_api_report_logger.info(f"""
<b>Rest Api Created</b>
^^^^^^^^^^^^^^^^
{self}
""", extra={'internal': True})

    def __str__(self):
        """ String representation of the RestApi instance """
        return f"""
{settings.logging.sub_point} Url         {settings.logging.key_val_sep} {self.url}
{settings.logging.sub_point} Headers     {settings.logging.key_val_sep} {self.headers}
{settings.logging.sub_point} Parameters  {settings.logging.key_val_sep} {self.parameters}
{settings.logging.sub_point} Body        {settings.logging.key_val_sep} {self.body}
{settings.logging.sub_point} Arguments   {settings.logging.key_val_sep} {self.kwargs}
"""

    async def _create_response(self, response: ClientResponse) -> RestApiResponse:
        """ Create response instance object from aiohttp async response """
        # Retrieve the response body in JSON
        # Only supports application/json content type
        body = await response.json() if response.content_type == 'application/json' else {}
        # Get the other response parameters
        status_code, headers, content_type = response.status, dict(response.headers), response.content_type
        # Create and return the RestApiResponse instance object
        rest_api_response = RestApiResponse(status_code=status_code,
                                            content_type=content_type,
                                            body=body,
                                            headers=headers,
                                            obj=response)
        # Logging
        test_rest_api_report_logger.info(f"""
<b>Rest Api Response</b>
^^^^^^^^^^^^^^^^^
{rest_api_response}
""", extra={'internal': True, '_increment_test_result_counts': 'responses'})
        return rest_api_response

    async def _send(self, method: str):
        """ Send the rest api by providing the request method """
        # Check if method is of type string
        if not isinstance(method, str):
            raise Exception(ErrorMsg.INVALID_METHOD_DATA_TYPE)
        # Convert to lowercase
        method = method.lower()
        # Check if the method is valid
        if method not in asdict(self.METHODS).values():
            raise Exception(ErrorMsg.INVALID_METHOD)
        # Logging
        test_rest_api_report_logger.info(f"""
<b>Rest Api Send</b>
^^^^^^^^^^^^^
{settings.logging.sub_point} Method {settings.logging.key_val_sep} {method.upper()}
""", extra={'internal': True, '_increment_test_result_counts': 'requests'})
        # Send the request
        async with getattr(self._session, method)(url=self.url,
                                                  params=self.parameters,
                                                  headers=self.headers,
                                                  json=self.body,
                                                  **self.kwargs) as response:
            return await self._create_response(response=response)

    @catch_exc_async(test_rest_api_exception=RestApiSendException)
    async def send(self, method: str):
        """ Send the rest api by providing the request method """
        return await self._send(method=method)

    @catch_exc_async(test_rest_api_exception=RestApiSendException)
    async def get(self):
        """ Send HTTP GET Request """
        return await self._send(method=self.METHODS.GET)

    @catch_exc_async(test_rest_api_exception=RestApiSendException)
    async def post(self):
        """ Send HTTP POST Request """
        return await self._send(method=self.METHODS.POST)

    @catch_exc_async(test_rest_api_exception=RestApiSendException)
    async def put(self):
        """ Send HTTP PUT Request """
        return await self._send(method=self.METHODS.PUT)

    @catch_exc_async(test_rest_api_exception=RestApiSendException)
    async def patch(self):
        """ Send HTTP PATCH Request """
        return await self._send(method=self.METHODS.PATCH)

    @catch_exc_async(test_rest_api_exception=RestApiSendException)
    async def delete(self):
        """ Send HTTP DELETE Request """
        return await self._send(method=self.METHODS.DELETE)

    @catch_exc_async(test_rest_api_exception=RestApiSendException)
    async def head(self):
        """ Send HTTP HEAD Request """
        return await self._send(method=self.METHODS.HEAD)

    @catch_exc_async(test_rest_api_exception=RestApiSendException)
    async def options(self):
        """ Send HTTP OPTIONS Request """
        return await self._send(method=self.METHODS.OPTIONS)
