import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import Literal, Optional, List, Dict, Any

from pipecat.transports.base_output import BaseOutputTransport

from connexity.client import ConnexityClient
from twilio.rest import Client
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    TTSTextFrame,
    TranscriptionFrame,
    CancelFrame,
    FunctionCallInProgressFrame,
    FunctionCallResultFrame,
    LLMFullResponseStartFrame,
    TTSStartedFrame, EndFrame,
)
from pipecat.observers.base_observer import BaseObserver, FramePushed
from pipecat.audio.vad.vad_analyzer import VADParams

from pipecat.processors.frame_processor import FrameDirection
from connexity.calls.base_call import BaseCall
from connexity.metrics.utils.twilio_module import TwilioCallManager
from connexity.calls.messages.user_message import UserMessage
from connexity.calls.messages.assistant_message import AssistantMessage
from connexity.calls.messages.tool_call_message import ToolCallMessage
from connexity.calls.messages.tool_result_message import ToolResultMessage
from connexity.metrics.utils.validate_json import validate_json

logger = logging.getLogger(__name__)

Role = Literal["user", "assistant", "tool_call"]


@dataclass
class Latency:
    tts: Optional[float] = None  # milliseconds
    llm: Optional[float] = None  # milliseconds
    stt: Optional[float] = None  # milliseconds
    vad: Optional[float] = None  # milliseconds

    def get_metrics(self):
        return {"tts": self.tts,
                "llm": self.llm,
                "stt": self.stt,
                "vad": self.vad}


@dataclass
class MessageData:
    role: Role
    start: Optional[float] = None  # seconds from call start
    end: Optional[float] = None    # seconds from call start
    content: str = ""
    latency: Optional[Latency] = None

    def has_valid_window(self) -> bool:
        return (
            self.start is not None
            and self.end is not None
            and self.content.strip() != ""
            and self.start < self.end
        )

    def reset(self) -> None:
        self.start = None
        self.end = None
        self.content = ""
        if self.latency:
            self.latency = Latency()  # reset subfields

    def get_metrics(self):
        return {"role": self.role,
                "start": self.start,
                "end": self.end,
                "content": self.content,
                "latency": self.latency}


@dataclass
class ToolCallData:
    role: Role = "tool_call"
    start: Optional[float] = None
    end: Optional[float] = None
    tool_call_id: Optional[str] = None
    function_name: Optional[str] = None
    arguments: Optional[str] = None
    content: str = ""


class InterfaceConnexityObserver(BaseObserver):

    MIN_SEPARATION = 0.5

    def __init__(self):
        super().__init__()
        self.call: BaseCall | None = None
        self.user_data = MessageData(role="user")
        self.assistant_data = MessageData(role="assistant", latency=Latency())
        self.tool_calls = ToolCallData()

        self.messages: List[Dict[str, Any]] = []

        # additional data for connexity
        self.sid = None
        self.twilio_client: Client | None = None
        self.final = False

        self.stt_start = None
        self.tts_start = None
        self.llm_start = None
        self.vad_stop_secs = None
        self.vad_start_secs = None

    @abstractmethod
    async def initialize(
        self,
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
        self.sid = sid
        self.twilio_client = TwilioCallManager(twilio_client)
        self.vad_stop_secs = vad_params.stop_secs
        self.vad_start_secs = vad_params.start_secs

        connexity_client = ConnexityClient(api_key=api_key)
        self.call = await connexity_client.register_call(
            sid=sid,
            agent_id=agent_id,
            user_phone_number=user_phone_number,
            agent_phone_number=agent_phone_number,
            created_at=None,
            voice_engine="pipecat",
            voice_provider=voice_provider,
            call_type=call_type,
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

    @staticmethod
    def _ns_to_s(ns: int) -> float:
        return ns / 1_000_000_000

    @staticmethod
    def _is_downstream_output(src: Any, direction: FrameDirection) -> bool:
        return isinstance(src, BaseOutputTransport) and direction == FrameDirection.DOWNSTREAM

    @staticmethod
    def _apply_min_separation(prev_time: Optional[float], current_time: float, min_sep: float) -> float:
        if prev_time is None or (current_time - prev_time) > min_sep:
            return current_time
        return prev_time

    def _debug(self, msg: str, **kv: Any) -> None:
        if kv:
            msg = f"{msg} | " + " ".join(f"{k}={v}" for k, v in kv.items())
        print("CONNEXITY SDK DEBUG | %s", msg, flush=True)

    # --- event handlers ------------------------------------------------------

    def _handle_latency_markers(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        # User finished speaking -> STT starts
        if isinstance(frame, UserStoppedSpeakingFrame):
            self.stt_start = t

        # LLM full response begins (first token) => close STT latency
        if isinstance(frame, LLMFullResponseStartFrame) and self._is_downstream_output(src, direction):
            if self.stt_start is not None and self.assistant_data.latency.stt is None:
                self.llm_start = t
                stt_ms = (t - self.stt_start) * 1000
                self.assistant_data.latency.stt = stt_ms
                self.stt_start = None
                self._debug("STT METRIC", ms=f"{stt_ms:.0f}")

        # TTS start => close LLM latency
        if isinstance(frame, TTSStartedFrame) and self._is_downstream_output(src,
                                                                             direction) and self.tts_start is None:
            if self.llm_start is not None:
                llm_ms = (t - self.llm_start) * 1000
                self.assistant_data.latency.llm = llm_ms
                self._debug("LLM METRIC", ms=f"{llm_ms:.0f}")
            self.tts_start = t

        # Bot audio actually starts => close TTS prepare latency
        if isinstance(frame, BotStartedSpeakingFrame) and self._is_downstream_output(src,
                                                                                     direction) and self.tts_start:
            tts_ms = (t - self.tts_start) * 1000
            self.assistant_data.latency.tts = tts_ms
            self.tts_start = None
            self._debug("TTS METRIC", ms=f"{tts_ms:.0f}")

    def _handle_bot_window(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        if not self._is_downstream_output(src, direction):
            return

        if isinstance(frame, BotStartedSpeakingFrame):
            self.assistant_data.start = self._apply_min_separation(
                self.assistant_data.start, t, self.MIN_SEPARATION
            )
            self._debug("BOT START SPEAKING", t=t)

        elif isinstance(frame, BotStoppedSpeakingFrame):
            self.assistant_data.end = self._apply_min_separation(
                self.assistant_data.end, t, self.MIN_SEPARATION
            )
            self._debug("BOT STOP SPEAKING", t=t)

    def _handle_user_window(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        if not self._is_downstream_output(src, direction):
            return

        if isinstance(frame, UserStartedSpeakingFrame):
            # include VAD pre-roll to approximate true start
            vad_start = t
            true_start = vad_start - (self.vad_start_secs or 0.0)
            self.user_data.start = true_start
            self._debug("USER START SPEAKING", t=t, true_start=true_start)

        elif isinstance(frame, UserStoppedSpeakingFrame):
            self.user_data.end = t
            self._debug("USER STOP SPEAKING", t=t)

    async def _handle_tool_call_start(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        if not (isinstance(frame, FunctionCallInProgressFrame) and self._is_downstream_output(src, direction)):
            return

        self.tool_calls.start = self._apply_min_separation(self.tool_calls.start, t, self.MIN_SEPARATION)
        self.tool_calls.tool_call_id = frame.tool_call_id
        self.tool_calls.function_name = frame.function_name
        self.tool_calls.arguments = frame.arguments

        await self.call.register_message(
            ToolCallMessage(
                arguments=frame.arguments,
                tool_call_id=frame.tool_call_id,
                content="",
                name=frame.function_name,
                seconds_from_start=t,
            )
        )
        self._debug("FUNCTION CALL STARTED",
                    tool_call_id=frame.tool_call_id, function=frame.function_name, args=str(frame.arguments))

    async def _handle_tool_call_end(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        if not (isinstance(frame, FunctionCallResultFrame) and self._is_downstream_output(src, direction)):
            return

        self.tool_calls.end = self._apply_min_separation(self.tool_calls.end, t, self.MIN_SEPARATION)
        self.tool_calls.content = frame.result

        is_json, json_data = validate_json(frame.result)
        await self.call.register_message(
            ToolResultMessage(
                content="",
                tool_call_id=frame.tool_call_id,
                result_type="JSON" if is_json else "string",
                result=json_data if is_json else frame.result,
                seconds_from_start=t,
            )
        )
        self._debug("FUNCTION CALL END",
                    tool_call_id=frame.tool_call_id, function=getattr(frame, "function_name", None))

    def _accumulate_content(self, frame: Any, src: Any, direction: FrameDirection) -> None:
        # STT text (guard against non-STT sources)
        if isinstance(frame, TranscriptionFrame) and getattr(src, "name", "").find("STTService") != -1:
            self.user_data.content += frame.text

        # TTS text (bot message accumulation)
        if isinstance(frame, TTSTextFrame) and self._is_downstream_output(src, direction):
            self.assistant_data.content += frame.text + " "

    async def _maybe_flush_user(self) -> None:
        if not self.user_data.has_valid_window():
            return

        self.messages.append(self.user_data.get_metrics())
        await self.call.register_message(
            UserMessage(
                content=self.user_data.content,
                seconds_from_start=self.user_data.start,
            )
        )
        self._debug("USER DATA COLLECTED", content_len=len(self.user_data.content or ""))
        self.user_data.reset()

    async def _maybe_flush_assistant(self) -> None:
        if not self.assistant_data.has_valid_window():
            return

        # VAD-based latency to first audio from end of last user utterance
        latency_ms: Optional[float] = None
        if self.messages and self.messages[-1].get("role") == "user":
            last_user_end_vad = self.messages[-1]["end"]
            real_end = last_user_end_vad - (self.vad_stop_secs or 0.0)
            latency_ms = (self.assistant_data.start - real_end) * 1000
            self.assistant_data.latency.vad = (self.vad_stop_secs or 0.0) * 1000

        self.messages.append(self.assistant_data.get_metrics())
        await self.call.register_message(
            AssistantMessage(
                content=self.assistant_data.content,
                time_to_first_audio=latency_ms,
                seconds_from_start=self.assistant_data.start,
                latency=self.assistant_data.latency.get_metrics(),
            )
        )
        self._debug("BOT DATA COLLECTED", content_len=len(self.assistant_data.content or ""),
                    t_start=self.assistant_data.start)
        self.assistant_data.reset()

        # --- main entry ----------------------------------------------------------

    async def on_push_frame(self, data: FramePushed) -> None:
        src = data.source
        frame = data.frame
        direction = data.direction
        t = self._ns_to_s(data.timestamp)

        # 1) latency anchors / metrics
        self._handle_latency_markers(frame, src, direction, t)

        # 2) speaking windows
        self._handle_bot_window(frame, src, direction, t)
        self._handle_user_window(frame, src, direction, t)

        # 3) tool-call lifecycle
        await self._handle_tool_call_start(frame, src, direction, t)
        await self._handle_tool_call_end(frame, src, direction, t)

        # 4) accumulate text content
        self._accumulate_content(frame, src, direction)

        # 5) flush messages if windows are valid
        await self._maybe_flush_user()
        await self._maybe_flush_assistant()

        # 6) handle cancellation (ensure finalization runs exactly once)
        if (isinstance(frame, CancelFrame) or isinstance(frame, EndFrame)) and not self.final:
            self.final = True
            await self.post_process_data()

    @abstractmethod
    async def post_process_data(self):
        ...
