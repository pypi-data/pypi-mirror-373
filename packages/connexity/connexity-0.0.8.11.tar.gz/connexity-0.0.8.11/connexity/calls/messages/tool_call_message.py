from typing import Optional

from connexity.calls.messages.interface_message import InterfaceMessage


class ToolCallMessage(InterfaceMessage):

    def __init__(self, content: str,
                 tool_call_id: str,
                 name: str,
                 seconds_from_start: Optional[float] = None,
                 arguments: Optional[dict] = None
                 ):
        super().__init__("tool_call", content, seconds_from_start)
        self.tool_call_id = tool_call_id
        self.name = name
        self.arguments = arguments

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "seconds_from_start": self.seconds_from_start,
            "tool_call_id": self.tool_call_id,
            "name": self.name,
            "arguments": self.arguments
        }
