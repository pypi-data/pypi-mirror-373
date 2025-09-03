from typing import Optional

from connexity.calls.messages.interface_message import InterfaceMessage


class AssistantMessage(InterfaceMessage):
    def __init__(self, content: str, time_to_first_audio: Optional[float] = None,
                 seconds_from_start: Optional[float] = None,
                 latency: Optional[dict] = None,
                 ):
        super().__init__("assistant", content, seconds_from_start)
        self.time_to_first_audio = time_to_first_audio
        if latency:
            self.latency = latency
        else:
            self.latency = {"stt": None, "llm": None, "tts": None}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "seconds_from_start": self.seconds_from_start,
            "time_to_first_audio": self.time_to_first_audio,
            "latency": self.latency
        }
