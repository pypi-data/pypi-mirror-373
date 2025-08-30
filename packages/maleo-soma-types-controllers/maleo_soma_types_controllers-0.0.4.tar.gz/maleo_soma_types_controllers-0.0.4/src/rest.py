from typing import Callable, TypeVar

ReturnT = TypeVar("ReturnT")
RESTController = Callable[..., ReturnT]
