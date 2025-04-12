from .api_ocr import online_ocr as online_ocr
from .ocr import recognize_image as local_ocr

__all__ = ["local_ocr", "online_ocr"]
