from pydantic import BaseModel
from typing import Optional

class TranscriptionResponse(BaseModel):
    success: bool
    text: str = ""
    error: Optional[str] = None