from .base_exception import TestRestApiException
from ..utils.decorator_hints import decorated_func_param_hints


@decorated_func_param_hints
def catch_exc(*, test_rest_api_exception: TestRestApiException):
    """
    Decorator used for catching python code exceptions for functions
    Example: Function calls with empty params, invalid params etc

    Developers can raise python Exceptions inside function body which will be auto converted to TestRestApiExceptions
    """

    def catch_exc_dec(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                raise test_rest_api_exception(msg=str(exc))

        return inner

    return catch_exc_dec


@decorated_func_param_hints
def catch_exc_async(*, test_rest_api_exception: TestRestApiException):
    """
    Decorator used for catching python code exceptions for async functions
    Example: Async function calls with empty params, invalid params etc

    Developers can raise python Exceptions inside async function body which will be auto converted to TestRestApiExceptions
    """

    def catch_exc_async_dec(func):
        async def inner(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                raise test_rest_api_exception(msg=str(exc), original=exc)

        return inner

    return catch_exc_async_dec
