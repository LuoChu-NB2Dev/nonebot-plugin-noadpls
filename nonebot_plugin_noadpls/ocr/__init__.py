from .api_ocr import api_paddle_ocr as online_ocr
from .ocr import recognize_image as local_ocr

__all__ = [
    "online_ocr", "local_ocr"
]
