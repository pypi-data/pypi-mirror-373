from ..runtime.runtime import Runtime
from ..utils.error_msg import ErrorMsg
from ..exceptions.decorators import catch_exc
from ..exceptions.constant_exception import ConstantException


class Constant(Runtime):
    """ Constant is same as Variable, but Immutable. Value cannot be changed once initialised """

    # Override Parent class Runtime -> Meta class to set data_type as 'Immutable'
    class Meta:
        data_type: str = 'Immutable'

    @catch_exc(test_rest_api_exception=ConstantException)
    def __getattribute__(self, attribute: str) -> any:
        """ Override __getattribute__ to get the attribute value """
        return super(Constant, self).__getattribute__(attribute)

    @catch_exc(test_rest_api_exception=ConstantException)
    def __setattr__(self, attr_name: str, attr_value: any) -> None:
        """ Override __setattr__ to set the attribute value """
        try:
            # Retrieve the value of the attribute
            value: any = super(Constant, self).__getattribute__(attr_name)
        except Exception:
            # If the attribute is not found, set value as None
            value: any = None
        finally:
            # If the attribute is already set, raise an exception
            if value:
                raise Exception(f'{ErrorMsg.CONSTANT_DUPLICATE}')
        # Set the attribute value
        super(Constant, self).__setattr__(attr_name, attr_value)


constant: Constant = Constant()
