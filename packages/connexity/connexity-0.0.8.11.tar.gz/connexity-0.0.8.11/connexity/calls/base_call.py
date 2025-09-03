import asyncio
import datetime
from typing import List, Optional, Literal

from connexity.calls.messages.interface_message import InterfaceMessage
from connexity.utils.send_data import send_data


class BaseCall:

    def __init__(self,
                 sid: str,
                 call_type: Literal["inbound", "outbound", "web"],
                 api_key: str,
                 agent_id: str,
                 user_phone_number: Optional[str] = None,
                 agent_phone_number: Optional[str] = None,
                 created_at=None,
                 voice_engine: Optional[str] = None,
                 transcriber: Optional[str] = None,
                 voice_provider: Optional[str] = None,
                 llm_model: Optional[str] = None,
                 llm_provider: Optional[str] = None,
                 phone_call_provider: Optional[str] = None,
                 stream: Optional[bool] = False,
                 env: Optional[Literal["production",
                                       "development"]] = 'development',
                 vad_analyzer: Optional[str] = None,
                 stt_model: Optional[str] = None,
                 tts_model: Optional[str] = None,
                 tts_voice: Optional[str] = None,
                 ):
        self._sid = sid
        self._call_type = call_type
        self._user_phone_number = user_phone_number
        self._agent_phone_number = agent_phone_number
        self._created_at = created_at
        self._agent_id = agent_id
        self._api_key = api_key
        self._voice_engine = voice_engine
        self._transcriber = transcriber
        self._stt_model = stt_model
        self._tts_model = tts_model
        self._tts_voice = tts_voice
        self._voice_provider = voice_provider
        self._llm_model = llm_model
        self._llm_provider = llm_provider
        self._phone_call_provider = phone_call_provider
        self._stream = stream
        self._run_mode = env
        self._vad_analyzer = vad_analyzer

        self._duration_in_seconds = None
        self._recording_url = None
        self._messages: List[InterfaceMessage] = []

    async def initialize(self):
        """Async method to handle post-init operations."""
        await self._send_data_to_connexity(update_type="status_update", status="in_progress", first=True)

    async def register_message(self, message: InterfaceMessage):
        self._messages.append(message)

        await self._send_data_to_connexity(update_type="conversation_update")

    async def update_last_message(self, message: InterfaceMessage):
        self._messages[-1] = message

        await self._send_data_to_connexity(update_type="conversation_update")

    async def init_post_call_data(self, recording_url: str, duration_in_seconds: float, created_at: datetime.datetime | None):
        self._recording_url = recording_url
        self._duration_in_seconds = duration_in_seconds
        self._created_at = created_at

        await self._send_data_to_connexity(update_type="conversation_update")
        await self._send_data_to_connexity(update_type="status_update", status="completed")
        await self._send_data_to_connexity(update_type="end_of_call")

    def _to_dict(self) -> dict:
        """
        Returns a JSON representation of the BaseCall instance.

        Returns:
            str: JSON string of the instance.
        """
        return {
            'sid': self._sid,
            'call_type': self._call_type,
            'user_phone_number': self._user_phone_number,
            'agent_phone_number': self._agent_phone_number,
            'created_at': self._created_at.isoformat() if hasattr(self._created_at, 'isoformat') else self._created_at,
            'agent_id': self._agent_id,
            'voice_engine': self._voice_engine,
            'transcriber': self._transcriber,
            'voice_provider': self._voice_provider,
            'llm_model': self._llm_model,
            'llm_provider': self._llm_provider,
            'phone_call_provider': self._phone_call_provider,
            'duration_in_seconds': self._duration_in_seconds,
            'recording_url': self._recording_url,
            'messages': [message.to_dict() for message in self._messages] if self._messages else [],
            "run_mode": self._run_mode,
            "vad_analyzer": self._vad_analyzer,
            "stt_model": self._stt_model,
            "tts_model": self._tts_model,
            "tts_voice": self._tts_voice,
        }

    async def _send_data_to_connexity(self, update_type: str, status: Optional[str] = None, first=False):
        """
        Sends accumulated data to Connexity's backend.

        Returns:
            dict: Response from the Connexity API.
        """

        data = self._to_dict()
        data['event_type'] = update_type
        data["status"] = status

        if update_type == "end_of_call":
            asyncio.create_task(send_data(data, self._api_key))
