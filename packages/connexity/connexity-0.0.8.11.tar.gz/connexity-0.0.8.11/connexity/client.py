from typing import Optional, Literal

from connexity.calls.base_call import BaseCall


class ConnexityClient:
    """
    ConnexityClient SDK for creating and managing calls.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key

    async def register_call(self, sid: str,
                            agent_id: str,
                            call_type: Literal["inbound", "outbound", "web"],
                            user_phone_number: Optional[str] = None,
                            agent_phone_number: Optional[str] = None,
                            created_at=None,
                            voice_engine: Optional[str] = None,
                            voice_provider: Optional[str] = None,
                            llm_model: Optional[str] = None,
                            llm_provider: Optional[str] = None,
                            phone_call_provider: Optional[str] = None,
                            transcriber: Optional[str] = None,
                            stream: Optional[bool] = False,
                            env: Optional[Literal["production",
                                                  "development"]] = 'development',
                            vad_analyzer: Optional[str] = None,
                            stt_model: Optional[str] = None,
                            tts_model: Optional[str] = None,
                            tts_voice: Optional[str] = None,
                            ) -> BaseCall:
        call: BaseCall = BaseCall(sid=sid,
                                  call_type=call_type,
                                  user_phone_number=user_phone_number,
                                  agent_phone_number=agent_phone_number,
                                  created_at=created_at,
                                  agent_id=agent_id,
                                  api_key=self.api_key,
                                  voice_engine=voice_engine,
                                  transcriber=transcriber,
                                  voice_provider=voice_provider,
                                  llm_model=llm_model,
                                  llm_provider=llm_provider,
                                  phone_call_provider=phone_call_provider,
                                  stream=stream,
                                  env=env,
                                  vad_analyzer=vad_analyzer,
                                  stt_model=stt_model,
                                  tts_model=tts_model,
                                  tts_voice=tts_voice
                                  )
        await call.initialize()
        return call
