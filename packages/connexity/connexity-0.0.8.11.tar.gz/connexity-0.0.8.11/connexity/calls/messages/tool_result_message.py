from typing import Optional

from connexity.calls.messages.interface_message import InterfaceMessage


class ToolResultMessage(InterfaceMessage):

    def __init__(self, content: str,
                 tool_call_id: str,
                 result_type: str,
                 seconds_from_start: Optional[float] = None,
                 result: Optional[str] = None
                 ):
        super().__init__("tool_result", content, seconds_from_start)
        self.tool_call_id = tool_call_id
        self.type = result_type
        self.result = result

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "seconds_from_start": self.seconds_from_start,
            "tool_call_id": self.tool_call_id,
            "type": self.type,
            "result": self.result
        }
