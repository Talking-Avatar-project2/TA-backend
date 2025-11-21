from pydantic import BaseModel

class FacialRecognitionRequest(BaseModel):
    image_data: bytes  # La imagen se enviará como datos binarios
