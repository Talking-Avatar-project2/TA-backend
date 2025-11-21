from pydantic import BaseModel
from typing import Optional

class FacialRecognitionResponse(BaseModel):
    detected_emotion: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
