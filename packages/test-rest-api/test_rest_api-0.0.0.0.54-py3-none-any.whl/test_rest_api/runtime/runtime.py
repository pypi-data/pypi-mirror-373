import re
from inspect import getframeinfo, stack
from test_rest_api import settings
from ..loggers.test_rest_api_report_logger import test_rest_api_report_logger


class Runtime:
    """
    Runtime is the base class for all the runtime variables
    """

    class Meta:
        data_type: str = 'Mutable'

    _create_title = lambda self: " ".join(re.findall("[A-Z][^A-Z]*", self.__class__.__name__))

    def __getattribute__(self, attribute: str) -> any:
        try:
            # Get the class attribute value
            # Call the base version of __getattribute__ you avoid the infinite recursive error
            value = super(Runtime, self).__getattribute__(attribute)
            # Get the caller object to retrieve the caller code
            caller = getframeinfo(stack()[3][0])
            # Get the caller code
            caller_code = caller.code_context[0].strip()
            # Only log for one condition. Example: my_value = variable.attribute
            if caller_code.endswith(f'.{attribute}'):
                # Logging
                self._log(title=f'Get {self._create_title()}',
                          code=caller_code,
                          result=f"{caller_code[:caller_code.find('=')]}= {value}",
                          data=f"{attribute} = {value}", )
            return value
        except Exception as exc:
            raise Exception(exc)

    def __setattr__(self, attr_name: str, attr_value: any):
        try:
            # Set the class attribute
            # Call the base version of __setattr__ you avoid the infinite recursive error
            super(Runtime, self).__setattr__(attr_name, attr_value)
            # Get the caller object to retrieve the caller code
            caller = getframeinfo(stack()[3][0])
            # Get the caller code
            caller_code = caller.code_context[0].strip()
            # Only log for one condition. Example: variable.attr_name = attr_value
            if f'.{attr_name}=' in caller_code.replace(' ', ''):
                # Logging
                self._log(title=f'Set {self._create_title()}',
                          code=caller_code,
                          result=f'Value set to {attr_value}',
                          data=f"{attr_name} = {attr_value}", )
        except Exception as exc:
            raise Exception(f'Exception: {exc}')

    def _log(self, title: str, code: str, result: str, data: str) -> None:
        test_rest_api_report_logger.info(f"""
<b>{title}</b>
{"^" * len(title)}
{settings.logging.sub_point} Code   {settings.logging.key_val_sep} {code}
{settings.logging.sub_point} Result {settings.logging.key_val_sep} {result}
{settings.logging.sub_point} Data   {settings.logging.key_val_sep} {data}
{settings.logging.sub_point} Type   {settings.logging.key_val_sep} {self.Meta.data_type}
""", extra={'internal': True})
