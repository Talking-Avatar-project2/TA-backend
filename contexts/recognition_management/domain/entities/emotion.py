from pydantic import BaseModel
from typing import Optional

class Emotion(BaseModel):
    detected_emotion: Optional[str] = None
    confidence: Optional[float] = None
