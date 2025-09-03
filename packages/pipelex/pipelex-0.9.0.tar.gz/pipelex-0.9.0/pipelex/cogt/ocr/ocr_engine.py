from pydantic import BaseModel

from pipelex.cogt.ocr.ocr_platform import OcrPlatform


class OcrEngine(BaseModel):
    ocr_platform: OcrPlatform
    ocr_model_name: str

    @property
    def desc(self) -> str:
        return f"Ocr Engine {self.ocr_platform}/{self.ocr_model_name}"
