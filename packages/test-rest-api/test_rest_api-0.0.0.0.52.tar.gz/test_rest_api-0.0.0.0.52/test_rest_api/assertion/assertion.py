from inspect import getframeinfo, stack
from .. import settings
from ..bug.bug import Bug
from ..exceptions.assertion_exception import AssertException
from ..utils.decorator_hints import decorated_func_param_hints
from ..loggers.test_rest_api_report_logger import test_rest_api_report_logger


@decorated_func_param_hints
def catch_exc(func):
    """
    Custom decorator just for Assert class methods

    Conditions
    ----------
    1. If an exception is raised, it should be Re-raised with AssertException.
       AssertException are raised when any unexpected exception occurs.
    2. If an AssertionError is raised, which happens when assert statement fails.
       This should NOT be treated as an exception and should NOT be Re-raised with AssertException
       Instead, it should be again asserted with FALSE and Bug obj passed
       This is done to raise the custom Bug obj passed in the assertion

    Assert class is created similar to python inbuilt assert statement
    Expectation is to raise python inbuilt AssertionError when the assertion fails with custom Bug obj
    """

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # AssertionError is raised, when assert statement failed
        except AssertionError as exc:
            # Perform the assertion again with FALSE and Bug obj passed
            # This is done to raise the custom Bug obj with AssertionError
            assert False, exc.args[0]
        # Any other exception is re raised as AssertException
        except Exception as exc:
            # Raise AssertException
            raise AssertException(msg=str(exc))

    return inner


class Assert:
    """
    Custom Assert Class for performing assertions
    Advantages of using this over python inbuilt assert statement -> Rich reporting for both pass and fail scenarios
    """

    @staticmethod
    def _log(*, code: str, assertion: str) -> None:
        """ Lof the assertion to the report """
        # Logging
        # Note: We are passing extra
        #       This is to auto update the report with the assertion counts
        #       This will update both summary level and individual test level assertion counts
        test_rest_api_report_logger.info(f"""
<b>Assertion</b>
^^^^^^^^^
{settings.logging.sub_point} Code   {settings.logging.key_val_sep} {code}
{settings.logging.sub_point} Assert {settings.logging.key_val_sep} {assertion}
""", extra={'internal': True, '_increment_test_result_counts': 'assertions'})

    @staticmethod
    def _assert(*, assertion, bug) -> None:
        """ Perform the assertion and log the assertion to the report """
        # Logging
        Assert._log(code=getframeinfo(stack()[4][0]).code_context[0].strip(), assertion=assertion)
        # Perform the assertion using python inbuilt assert statement
        exec(f'{assertion}, bug')

    @staticmethod
    def _format_args(func):
        def inner(*args, **kwargs):
            """
            This is done to avoid error caused by strings, in exec() function
            Convert string values to 'VALUE' by adding single quotes to the value
            """
            # Format the args
            args = [
                f"'''{arg}'''" if isinstance(arg, str) and '\n' in arg else f"'{arg}'" if isinstance(arg, str) else arg
                for arg in args]
            # Format the kwargs
            kwargs = {
                key: f"'''{value}'''" if isinstance(value, str) and '\n' in value else f"'{value}'" if isinstance(value,
                                                                                                                  str) else value
                for key, value in kwargs.items()}
            func(*args, **kwargs)

        return inner

    @staticmethod
    @catch_exc
    @_format_args
    def equal(arg1: any, arg2: any, bug: Bug = Bug()) -> None:
        """
        Check if arg1 == arg2
        Raise your custom Bug if needed
        """
        Assert._assert(assertion=f'assert {arg1} == {arg2}', bug=bug)

    @staticmethod
    @catch_exc
    @_format_args
    def not_equal(arg1: any, arg2: any, bug: Bug = Bug()) -> None:
        """
        Check if arg1 != arg2
        Raise your custom Bug if needed
        """
        Assert._assert(assertion=f'assert {arg1} != {arg2}', bug=bug)

    @staticmethod
    @catch_exc
    @_format_args
    def true(arg: any, bug: Bug = Bug()):
        """
        Check if arg == True
        Raise your custom Bug if needed
        """
        Assert._assert(assertion=f'assert {arg}', bug=bug)

    @staticmethod
    @catch_exc
    @_format_args
    def false(arg: any, bug: Bug = Bug()):
        """
        Check if arg == False
        Raise your custom Bug if needed
        """
        Assert._assert(assertion=f'assert not {arg}', bug=bug)

    @staticmethod
    @catch_exc
    @_format_args
    def greater(arg1: any, arg2: any, bug: Bug = Bug()):
        """
        Check if arg1 > arg2
        Raise your custom Bug if needed
        """
        Assert._assert(assertion=f'assert {arg1} > {arg2}', bug=bug)

    @staticmethod
    @catch_exc
    @_format_args
    def lesser(arg1: any, arg2: any, bug: Bug = Bug()):
        """
        Check if arg1 < arg2
        Raise your custom Bug if needed
        """
        Assert._assert(assertion=f'assert {arg1} < {arg2}', bug=bug)

    @staticmethod
    @catch_exc
    @_format_args
    def greater_equal(arg1: any, arg2: any, bug: Bug = Bug()):
        """
        Check if arg1 >= arg2
        Raise your custom Bug if needed
        """
        Assert._assert(assertion=f'assert {arg1} >= {arg2}', bug=bug)

    @staticmethod
    @catch_exc
    @_format_args
    def lesser_equal(arg1: any, arg2: any, bug: Bug = Bug()):
        """
        Check if arg1 <= arg2
        Raise your custom Bug if needed
        """
        Assert._assert(assertion=f'assert {arg1} <= {arg2}', bug=bug)
