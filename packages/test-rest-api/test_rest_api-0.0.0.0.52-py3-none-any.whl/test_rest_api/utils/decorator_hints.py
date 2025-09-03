from typing import Callable


def decorated_func_param_hints(decorator: Callable) -> Callable:
    """
    Decorate decorator functions to get the function parameter hints instead of showing *args, **kwargs in pycharm
    """
    return decorator
