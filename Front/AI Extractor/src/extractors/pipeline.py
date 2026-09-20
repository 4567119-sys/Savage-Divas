import time
from typing import List, Any
from pypdf import PdfReader
import io

from .base import is_pdf, is_image
from .local_extractor import LocalHeuristicExtractor
from .gemini_extractor import GeminiVisionExtractor

from ..schemas import (
    ExtractionResponse,
    ExtractionData,
    AccidentReportData,
    ProcessingMetadata,
)

from ..config import settings


class DocumentExtractionPipeline:
    """
    Main extraction orchestrator.

    Uses Gemini Vision AI when configured and falls back to the
    local heuristic extractor when Gemini is unavailable or fails.

    The pipeline supports both:
    - General Royal Square Financial requests
    - Existing accident / police report extraction
    """

    def __init__(self):
        self.local_extractor = LocalHeuristicExtractor()
        self.gemini_extractor = None

        if settings.has_gemini:
            try:
                self.gemini_extractor = GeminiVisionExtractor()
            except Exception as e:
                print(f"[Pipeline] Warning initializing GeminiExtractor: {e}")

    async def process_document(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        force_engine: str = "auto",
    ) -> ExtractionResponse:

        start_time = time.time()
        file_size = len(file_bytes)
        pages_count = 1

        # ---------------------------------------------------------
        # Determine number of PDF pages
        # ---------------------------------------------------------
        if is_pdf(filename, content_type):
            try:
                reader = PdfReader(io.BytesIO(file_bytes))
                pages_count = len(reader.pages)
            except Exception:
                pages_count = 1

        raw_text_excerpt = ""
        engine_used = "local_heuristic_extractor"
        used_fallback = False
        warnings: List[str] = []

        # ---------------------------------------------------------
        # Decide whether Gemini should be used
        # ---------------------------------------------------------
        should_use_gemini = (
            force_engine == "gemini"
            or (
                force_engine == "auto"
                and settings.has_gemini
            )
        )

        # ---------------------------------------------------------
        # Extract document
        # ---------------------------------------------------------
        if should_use_gemini:

            try:
                if not self.gemini_extractor:
                    self.gemini_extractor = GeminiVisionExtractor()

                extracted_data, raw_text_excerpt = await (
                    self.gemini_extractor.extract(
                        file_bytes,
                        filename,
                        content_type,
                    )
                )

                engine_used = settings.GEMINI_MODEL

            except Exception as e:

                warnings.append(
                    f"Primary vision AI extraction failed ({str(e)}); "
                    "using local fallback engine."
                )

                used_fallback = True

                extracted_data, raw_text_excerpt = await (
                    self.local_extractor.extract(
                        file_bytes,
                        filename,
                        content_type,
                    )
                )

                engine_used = "local_heuristic_extractor (fallback)"

        else:

            if (
                not settings.has_gemini
                and is_image(filename, content_type)
            ):
                warnings.append(
                    "Image uploaded without GEMINI_API_KEY. "
                    "For full image/scanned OCR, configure "
                    "GEMINI_API_KEY in .env."
                )

            extracted_data, raw_text_excerpt = await (
                self.local_extractor.extract(
                    file_bytes,
                    filename,
                    content_type,
                )
            )

            engine_used = "local_heuristic_extractor"

        # ---------------------------------------------------------
        # Convert old extractor output into the new general format
        # ---------------------------------------------------------
        data = self._normalize_data(extracted_data)

        # ---------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------
        overall_confidence = self._calculate_overall_confidence(data)

        self._check_confidence_warnings(
            data,
            warnings,
        )

        # ---------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------
        duration_ms = int(
            (time.time() - start_time) * 1000
        )

        metadata = ProcessingMetadata(
            filename=filename,
            file_size_bytes=file_size,
            content_type=content_type,
            pages_processed=pages_count,
            processing_time_ms=duration_ms,
            extraction_engine=engine_used,
            used_fallback=used_fallback,
            document_type_detected=self._detect_document_type(data),
        )

        # ---------------------------------------------------------
        # Final API response
        # ---------------------------------------------------------
        return ExtractionResponse(
            success=True,
            overall_confidence=overall_confidence,
            data=data,
            raw_text_excerpt=raw_text_excerpt,
            warnings=warnings,
            metadata=metadata,
        )

    # =============================================================
    # DATA NORMALIZATION
    # =============================================================

    def _normalize_data(self, extracted_data: Any) -> ExtractionData:
        """
        Converts extractor output into the new ExtractionData format.

        This keeps the existing accident extractor working while
        allowing the system to support all Royal Square services.
        """

        # New extractor already returns ExtractionData
        if isinstance(extracted_data, ExtractionData):
            return extracted_data

        # Existing extractor still returns AccidentReportData
        if isinstance(extracted_data, AccidentReportData):

            data = ExtractionData()

            data.accident = extracted_data

            # Existing accident reports are normally personal
            # insurance claims unless the document indicates otherwise.
            data.classification.service_type = "personal_insurance"

            data.classification.request_type = "claim"

            data.classification.request_subtype = "accident_claim"

            data.classification.classification_confidence = 0.90

            # Copy useful insurance information
            data.insurance.insurance_category.value = (
                "Personal Insurance"
            )
            data.insurance.insurance_category.confidence = 0.90

            data.insurance.claim_type.value = (
                "Accident Claim"
            )
            data.insurance.claim_type.confidence = 0.90

            return data

        # If something unexpected is returned, create an empty
        # general response rather than crashing the API.
        return ExtractionData()

    # =============================================================
    # CONFIDENCE
    # =============================================================

    def _calculate_overall_confidence(
        self,
        data: ExtractionData,
    ) -> float:

        classification_confidence = (
            data.classification.classification_confidence
        )

        # ---------------------------------------------------------
        # General Royal Square request
        # ---------------------------------------------------------
        general_confidences = []

        general_fields = [
            data.general.client_name,
            data.general.client_reference,
            data.general.policy_number,
            data.general.request_date,
            data.general.requested_action,
            data.general.client_request_summary,
        ]

        for field in general_fields:
            if field is not None and field.value:
                general_confidences.append(
                    field.confidence
                )

        # ---------------------------------------------------------
        # Investment information
        # ---------------------------------------------------------
        investment_fields = [
            data.investment.monthly_investment_amount,
            data.investment.investment_time_horizon,
            data.investment.investment_goal_name,
            data.investment.target_amount,
            data.investment.target_date,
        ]

        for field in investment_fields:
            if field is not None and field.value:
                general_confidences.append(
                    field.confidence
                )

        # ---------------------------------------------------------
        # Insurance information
        # ---------------------------------------------------------
        insurance_fields = [
            data.insurance.insurance_category,
            data.insurance.policy_number,
            data.insurance.claim_type,
        ]

        for field in insurance_fields:
            if field is not None and field.value:
                general_confidences.append(
                    field.confidence
                )

        # ---------------------------------------------------------
        # Accident information
        # ---------------------------------------------------------
        accident_fields = [
            data.accident.case_number,
            data.accident.police_station,
            data.accident.officer_name,
            data.accident.incident_date,
        ]

        for field in accident_fields:
            if field is not None and field.value:
                general_confidences.append(
                    field.confidence
                )

        # Nothing was extracted
        if not general_confidences:
            return round(
                min(
                    1.0,
                    max(
                        0.0,
                        classification_confidence,
                    ),
                ),
                2,
            )

        extracted_average = sum(
            general_confidences
        ) / len(general_confidences)

        # Classification is important, so give it strong weight.
        if classification_confidence > 0:
            score = (
                classification_confidence * 0.40
                + extracted_average * 0.60
            )
        else:
            score = extracted_average

        return round(
            min(1.0, max(0.0, score)),
            2,
        )

    # =============================================================
    # WARNINGS
    # =============================================================

    def _check_confidence_warnings(
        self,
        data: ExtractionData,
        warnings: List[str],
    ):

        threshold = settings.CONFIDENCE_THRESHOLD

        # ---------------------------------------------------------
        # Classification warning
        # ---------------------------------------------------------
        classification = data.classification

        if classification.service_type == "unknown":
            warnings.append(
                "Royal Square service type could not be confidently "
                "identified."
            )

        elif (
            classification.classification_confidence
            < threshold
        ):
            warnings.append(
                "Service classification has low confidence "
                f"({classification.classification_confidence:.2f} "
                f"< {threshold:.2f}). Please verify."
            )

        # ---------------------------------------------------------
        # General fields
        # ---------------------------------------------------------
        fields = [
            ("Client Name", data.general.client_name),
            ("Policy Number", data.general.policy_number),
            ("Requested Action", data.general.requested_action),
            (
                "Client Request Summary",
                data.general.client_request_summary,
            ),
        ]

        for name, field in fields:

            if field is None:
                continue

            if field.value and field.confidence < threshold:
                warnings.append(
                    f"{name} extracted with low confidence "
                    f"({field.confidence:.2f} < "
                    f"{threshold:.2f}). Please verify."
                )

        # ---------------------------------------------------------
        # Accident-specific warnings
        # ---------------------------------------------------------
        if (
            classification.request_type == "claim"
            and classification.request_subtype
            and "accident" in classification.request_subtype
        ):

            accident_fields = [
                ("Case Number", data.accident.case_number),
                ("Police Station", data.accident.police_station),
                ("Officer Name", data.accident.officer_name),
                ("Incident Date", data.accident.incident_date),
            ]

            for name, field in accident_fields:

                if not field.value:
                    warnings.append(
                        f"{name} could not be detected "
                        "in the document."
                    )

                elif field.confidence < threshold:
                    warnings.append(
                        f"{name} extracted with low confidence "
                        f"({field.confidence:.2f} < "
                        f"{threshold:.2f}). Please verify."
                    )

    # =============================================================
    # DOCUMENT TYPE
    # =============================================================

    def _detect_document_type(
        self,
        data: ExtractionData,
    ) -> str:

        service = data.classification.service_type
        request = data.classification.request_type
        subtype = data.classification.request_subtype

        # Accident claim
        if (
            request == "claim"
            and subtype
            and "accident" in subtype
        ):
            return "accident_police_report"

        # Insurance
        if service in [
            "life_insurance",
            "funeral_insurance",
            "health_insurance",
            "personal_insurance",
            "commercial_insurance",
        ]:
            return "insurance_document"

        # Financial planning
        if service == "financial_planning":
            return "financial_planning_request"

        # Goal-based investment
        if service == "goal_based_investment":
            return "investment_goal_request"

        # General investment
        if service == "investment":
            return "investment_request"

        # General client request
        if service == "general_service":
            return "client_request"

        return "unknown"