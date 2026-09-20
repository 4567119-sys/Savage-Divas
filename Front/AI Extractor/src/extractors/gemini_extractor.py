import json
from typing import Tuple, Optional
from google import genai
from google.genai import types

from .base import BaseExtractor, is_pdf, is_image
from ..schemas import AccidentReportData
from ..config import settings

EXTRACTION_SYSTEM_INSTRUCTION = """
You are an expert document intelligence AI specialized in parsing South African Police Service (SAPS) and international police accident reports, crash reports, and accident statement dockets.

Analyze the uploaded document (which may contain scans, handwriting, stamps, or multi-column forms).
Your task is to accurately extract the core accident claim information into the requested schema:
1. case_number: The official CAS number (e.g. CAS 123/04/2024), OAR number, or Reference/Docket number.
2. police_station: Name of the reporting police station or precinct (e.g. 'Sandton SAPS', 'Johannesburg Central').
3. officer_name: Name, rank, and badge/force number of the reporting officer (e.g. 'Sgt. K. Sithole', 'Constable Dlamini').
4. incident_date: Date the incident occurred, strictly formatted as YYYY-MM-DD.
5. incident_time: Time of the accident (e.g. '14:30' or '08h15').
6. incident_location: Street address, intersection, or physical location.
7. incident_description: Concise summary of what happened according to the report.
8. damages_summary: Observed or reported vehicular/property damage.
9. vehicles_involved: List of vehicles with make/model, license plate / registration number, and driver name.
10. parties_involved: Key drivers, passengers, or witnesses mentioned.

Confidence Scoring Guidelines:
- Assign confidence 0.90 to 1.00 for clear, unambiguous typed text.
- Assign confidence 0.70 to 0.89 for legible handwriting or partially obscured stamps.
- Assign confidence 0.30 to 0.69 if guessed from context or partially degraded text.
- If a field is missing from the document, set its value to null and confidence to 0.0.
"""

class GeminiVisionExtractor(BaseExtractor):
    """
    Multimodal Vision & Document Intelligence extractor powered by Gemini Flash models.
    Supports scanned PDFs, multi-page forms, handwriting, and photos.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.client = genai.Client(api_key=self.api_key)

    async def extract(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str
    ) -> Tuple[AccidentReportData, Optional[str]]:
        mime_type = self._determine_mime_type(filename, content_type)

        part = types.Part.from_bytes(
            data=file_bytes,
            mime_type=mime_type
        )

        prompt = (
            "Extract all police and accident report details from this document. "
            "Ensure case number, police station, officer name, and incident date are identified with high accuracy."
        )

        config = types.GenerateContentConfig(
            system_instruction=EXTRACTION_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=AccidentReportData,
            temperature=0.1
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[part, prompt],
            config=config
        )

        # Parse output
        raw_text = response.text or ""
        try:
            if hasattr(response, "parsed") and response.parsed:
                return response.parsed, raw_text[:1200]
            data_dict = json.loads(raw_text)
            data = AccidentReportData.model_validate(data_dict)
            return data, raw_text[:1200]
        except Exception as e:
            # Fallback parsing
            data_dict = json.loads(raw_text)
            return AccidentReportData(**data_dict), raw_text[:1200]

    def _determine_mime_type(self, filename: str, content_type: str) -> str:
        fn = filename.lower()
        if is_pdf(filename, content_type):
            return "application/pdf"
        elif fn.endswith(".png") or content_type == "image/png":
            return "image/png"
        elif fn.endswith(".jpg") or fn.endswith(".jpeg") or content_type in ("image/jpeg", "image/jpg"):
            return "image/jpeg"
        elif fn.endswith(".webp") or content_type == "image/webp":
            return "image/webp"
        elif fn.endswith(".txt") or content_type == "text/plain":
            return "text/plain"
        return content_type or "application/octet-stream"
