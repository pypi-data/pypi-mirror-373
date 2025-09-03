from typing import Optional

from connexity.calls.messages.interface_message import InterfaceMessage


class UserMessage(InterfaceMessage):

    def __init__(self, content: str,
                 seconds_from_start: Optional[float] = None,
                 is_interruption: Optional[bool] = None
                 ):
        super().__init__("user", content, seconds_from_start)
        self.is_interruption = is_interruption

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "seconds_from_start": self.seconds_from_start,
            "is_interruption": self.is_interruption
        }
