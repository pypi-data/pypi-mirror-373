from abc import abstractmethod
from typing import Optional, Literal
import uuid


class InterfaceMessage:
    """
    Represents a single message with specific attributes.
    """

    def __init__(self, role: Literal["system", "assistant", "user", "tool_call", "tool_result"], content: str, seconds_from_start: Optional[float] = None):
        self.id = role + '-' + str(seconds_from_start) if seconds_from_start else str(uuid.uuid4())
        self.role = role
        self.content = content
        self.seconds_from_start = seconds_from_start

    @abstractmethod
    def to_dict(self) -> dict:
        pass

