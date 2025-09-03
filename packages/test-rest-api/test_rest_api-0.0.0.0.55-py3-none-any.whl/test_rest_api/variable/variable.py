from ..runtime.runtime import Runtime
from ..exceptions.decorators import catch_exc
from ..exceptions.variable_exception import VariableException


class Variable(Runtime):
    """
    Variable can be used for correlations in tests
    """

    class Meta:
        data_type: str = 'Mutable'

    @catch_exc(test_rest_api_exception=VariableException)
    def __getattribute__(self, attribute: str) -> any:
        return super(Variable, self).__getattribute__(attribute)

    @catch_exc(test_rest_api_exception=VariableException)
    def __setattr__(self, attr_name: str, attr_value: any) -> None:
        super(Variable, self).__setattr__(attr_name, attr_value)


variable = Variable()
