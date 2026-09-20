import io
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from pypdf import PdfReader
from PIL import Image

from ..schemas import AccidentReportData

class BaseExtractor(ABC):
    """Abstract base class for document extraction engines."""

    @abstractmethod
    async def extract(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str
    ) -> Tuple[AccidentReportData, Optional[str]]:
        """
        Extract structured accident/police data from raw file bytes.
        Returns: (AccidentReportData, raw_text_or_summary)
        """
        pass

def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
    """Extracts raw text and page count from a PDF file using pypdf."""
    stream = io.BytesIO(file_bytes)
    reader = PdfReader(stream)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)
    full_text = "\n\n--- PAGE BREAK ---\n\n".join(pages_text)
    return full_text.strip(), len(reader.pages)

def is_pdf(filename: str, content_type: str) -> bool:
    return content_type == "application/pdf" or filename.lower().endswith(".pdf")

def is_image(filename: str, content_type: str) -> bool:
    image_exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")
    return content_type.startswith("image/") or any(filename.lower().endswith(ext) for ext in image_exts)
