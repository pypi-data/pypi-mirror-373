from dataclasses import dataclass


@dataclass(frozen=True)
class RestApiMethod:
    """
    List of supported aiohttp request methods
    HTTP defines a set of request methods to indicate the desired action to be performed for a given resource.
    """
    GET: str = 'get'
    POST: str = 'post'
    PUT: str = 'put'
    PATCH: str = 'patch'
    DELETE: str = 'delete'
    HEAD: str = 'head'
    OPTIONS: str = 'options'
