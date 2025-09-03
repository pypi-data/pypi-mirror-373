import json
import time
import logging
from functools import wraps
from math import trunc

from connexity.CONST import CONNEXITY_METRICS_URL
from connexity.utils.send_data import send_data
from fastapi.responses import StreamingResponse
from connexity.metrics.schemas import ElevenlabsRequestBody
from connexity.metrics.utils import contains_full_sentence

logger = logging.getLogger(__name__)


def measure_first_chunk_latency():
    """
    Decorator for FastAPI endpoints that return a StreamingResponse.
    Logs the time to the first sentence (TTFS) from when the endpoint
    function is invoked, and sends the first sentence plus ~50 more characters.
    """
    def actual_decorator(method):
        @wraps(method)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            data: ElevenlabsRequestBody = kwargs.get("request_body")
            try:
                sid = data.elevenlabs_extra_body.get("sid") if data else None
            except Exception:
                sid = None
            original_response = await method(*args, **kwargs)

            if not isinstance(original_response, StreamingResponse):
                return original_response

            async def wrapped_body_iterator():
                first_sentence_sent = False
                sentence_accum = ""
                sentence_complete = False
                base_sentence_length = 0
                latency = None

                async for chunk in original_response.body_iterator:
                    if sid:
                        try:
                            if not first_sentence_sent:
                                data = chunk[5:]
                                data = json.loads(data)
                                new_content = data.get("choices")[0].get("delta", {}).get("content", "")
                                sentence_accum += new_content

                                # Detect the end of the first sentence
                                if not sentence_complete and contains_full_sentence(sentence_accum):
                                    sentence_complete = True
                                    latency = time.time() - start_time
                                    base_sentence_length = len(sentence_accum)

                                # If sentence is done and we got 50+ more chars, round to word and send
                                if sentence_complete and len(sentence_accum) >= base_sentence_length + 50:
                                    rounded = round_to_last_word(sentence_accum[:base_sentence_length + 50])
                                    data_dict = {
                                        "sid": sid,
                                        "latency": trunc(latency * 1000),
                                        "first_sentence": rounded.strip()
                                    }
                                    await send_data(data_dict, api_key='none', url=CONNEXITY_METRICS_URL)
                                    first_sentence_sent = True

                        except Exception as e:
                            logger.exception(f"Exception while processing chunk: {e}")

                    yield chunk

                # If stream ends before we reach +50 characters
                if sentence_complete and not first_sentence_sent and sid:
                    rounded = round_to_last_word(sentence_accum)
                    data_dict = {
                        "sid": sid,
                        "latency": trunc(latency * 1000),
                        "first_sentence": rounded.strip()
                    }
                    await send_data(data_dict, api_key='none', url=CONNEXITY_METRICS_URL)

            def round_to_last_word(text):
                words = text.split(" ")
                return " ".join(words).strip()

            new_response = StreamingResponse(
                wrapped_body_iterator(),
                media_type=original_response.media_type
            )

            new_response.status_code = original_response.status_code
            new_response.headers.update(original_response.headers)

            return new_response

        return wrapper

    return actual_decorator
