from typing import Literal

from connexity.client import ConnexityClient
from pipecat.audio.vad.vad_analyzer import VADParams
from twilio.rest import Client

from connexity.metrics.pipecat_interface import InterfaceConnexityObserver

from connexity.metrics.utils.get_daily_recording_url import get_daily_recording_url


class ConnexityDailyObserver(InterfaceConnexityObserver):

    async def initialize(self,
                         sid: str,
                         agent_id: str,
                         api_key: str,
                         voice_provider: str,
                         llm_provider: str,
                         llm_model: str,
                         stt_model: str,
                         tts_model: str,
                         tts_voice: str,
                         call_type: Literal["inbound", "outbound", "web"],
                         transcriber: str,
                         vad_params: VADParams,
                         env: Literal["development", "production"],
                         vad_analyzer: str,
                         phone_call_provider: str = None,
                         user_phone_number: str = None,
                         agent_phone_number: str = None,
                         twilio_client: Client = None,
                         daily_api_key: str = None
                         ):
        if not daily_api_key:
            raise ValueError("DAILY API KEY NOT PROVIDED")
        self.vad_stop_secs = vad_params.stop_secs
        self.vad_start_secs = vad_params.start_secs
        self.sid = sid
        self.daily_api_key = daily_api_key
        connexity_client = ConnexityClient(api_key=api_key)
        self.call = await connexity_client.register_call(
            sid=sid,
            agent_id=agent_id,
            user_phone_number=user_phone_number,
            agent_phone_number=agent_phone_number,
            created_at=None,
            voice_engine='daily',
            voice_provider=voice_provider,
            call_type="web",
            llm_provider=llm_provider,
            llm_model=llm_model,
            phone_call_provider=phone_call_provider,
            transcriber=transcriber,
            stt_model=stt_model,
            tts_model=tts_model,
            tts_voice=tts_voice,
            stream=False,
            env=env,
            vad_analyzer=vad_analyzer
        )

    async def post_process_data(self):
        recording_url, duration = get_daily_recording_url(self.daily_api_key, self.sid)
        print('CONNEXITY SDK DEBUG| CALL COLLECTED DATA:', flush=True)
        print(self.messages, flush=True)

        await self.call.init_post_call_data(recording_url=recording_url, created_at=None,
                                            duration_in_seconds=duration)


