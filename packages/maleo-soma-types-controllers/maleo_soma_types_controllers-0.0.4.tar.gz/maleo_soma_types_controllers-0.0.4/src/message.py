from google.cloud.pubsub_v1.subscriber.message import Message
from typing import Callable, TypeVar

ReturnT = TypeVar("ReturnT")
MessageController = Callable[[Message], ReturnT]
