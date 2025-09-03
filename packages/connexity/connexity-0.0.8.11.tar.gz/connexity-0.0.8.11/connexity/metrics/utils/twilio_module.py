from asyncio import sleep
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


class TwilioCallManager:
    def __init__(self, client: Client):
        self.client = client
        self.account_sid = client.username

    async def get_call_duration(self, call_sid: str) -> int | None:
        """
        Fetches the call duration. On any error, logs and returns None.
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return call.duration
        except TwilioRestException as e:
            print(
                f"CONNEXITY SDK DEBUG| Error fetching call duration [{e.status}] {e.msg}",
                flush=True
            )
        except Exception as e:
            print(
                f"CONNEXITY SDK DEBUG| Unexpected error fetching call duration: {e}",
                flush=True
            )
        return None

    async def get_call_recording_url(
            self,
            call_sid: str,
            *,
            max_retries: int = 3,
            delay_sec: int = 3
    ) -> str | None:
        """
        Try fetching the specific recording you just created.
        Retry up to max_retries times on 404.
        """
        for attempt in range(1, max_retries + 1):
            try:
                recordings = self.client.recordings.list(call_sid=call_sid)
                if recordings:
                    return f"{recordings[0].media_url}.wav"
            except TwilioRestException as e:
                if e.status == 404:
                    print(
                        f"CONNEXITY SDK DEBUG| Attempt {attempt} got 404; retrying in {delay_sec}s…",
                        flush=True
                    )
                else:
                    print(
                        f"CONNEXITY SDK DEBUG| Unexpected error: {e}",
                        flush=True
                    )
                    return None

                if attempt < max_retries:
                    await sleep(delay_sec)
        print(
            f"CONNEXITY SDK DEBUG| Giving up after {max_retries} attempts",
            flush=True
        )
        return None

    async def get_start_call_data(self, call_sid: str) -> str | None:
        """
        Fetches the call’s start_time in ISO format. On error, logs and returns None.
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return call.start_time.isoformat().replace("+00:00", "Z")
        except TwilioRestException as e:
            print(
                f"CONNEXITY SDK DEBUG| Error fetching start time [{e.status}]: {e.msg}",
                flush=True
            )
        except Exception as e:
            print(
                f"CONNEXITY SDK DEBUG| Unexpected error fetching start time: {e}",
                flush=True
            )
        return None
