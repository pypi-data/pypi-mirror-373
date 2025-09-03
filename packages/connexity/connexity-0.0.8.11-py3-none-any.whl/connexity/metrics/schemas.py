from typing import List, Optional, Dict

from pydantic import BaseModel


class ElevenlabsRequestBody(BaseModel):
    messages: List
    model: str
    max_tokens: int
    stream: bool
    temperature: float
    tools: Optional[List[Dict]]
    elevenlabs_extra_body: Optional[Dict] = None
