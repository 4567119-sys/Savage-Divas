import re
from datetime import datetime
from typing import Tuple, Optional, List

from .base import BaseExtractor, extract_text_from_pdf, is_pdf, is_image
from ..schemas import (
    ExtractionData,
    ExtractedField,
    ExtractedVehicle,
    ExtractedParty,
)


# Common South African police station references
KNOWN_STATIONS = [
    "sandton", "johannesburg central", "jhb central", "pretoria central",
    "cape town central", "durban central", "randburg", "midrand",
    "rosebank", "soweto", "kempton park", "centurion", "gqeberha central",
    "bloemfontein", "bellville", "stellenbosch", "brooklyn", "sunnyside",
    "linden", "alexandra", "norwood", "brixton", "hillbrow", "parkview",
]


COMMON_VEHICLE_MAKES = [
    "toyota", "volkswagen", "vw", "ford", "bmw", "mercedes",
    "mercedes-benz", "nissan", "hyundai", "honda", "isuzu", "audi",
    "renault", "suzuki", "kia", "mazda", "chevrolet", "mitsubishi",
    "haval", "chery",
]


class LocalHeuristicExtractor(BaseExtractor):
    """
    Local rule-based extractor.

    This extractor works without an AI API key and supports:
    - insurance requests
    - financial planning requests
    - investment requests
    - goal-based investment requests
    - accident / police reports
    - general client requests

    It returns the new ExtractionData structure used by the
    generalized Royal Square Financial AI pipeline.
    """

    async def extract(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> Tuple[ExtractionData, Optional[str]]:

        raw_text = ""

        if is_pdf(filename, content_type):
            try:
                raw_text, _ = extract_text_from_pdf(file_bytes)
            except Exception as e:
                raw_text = f"[Error reading PDF text: {e}]"

        elif is_image(filename, content_type):
            raw_text = (
                "[Image document uploaded. Local text parser requires text content; "
                "use Gemini multimodal vision for visual OCR.]"
            )
            return ExtractionData(), raw_text

        else:
            try:
                raw_text = file_bytes.decode("utf-8", errors="ignore")
            except Exception:
                raw_text = ""

        data = self._parse_text(raw_text)

        return data, raw_text[:1200]

    def _parse_text(self, text: str) -> ExtractionData:
        data = ExtractionData()

        if not text or text.startswith("["):
            return data

        # Normalize text for easier keyword matching.
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        full_text = " ".join(lines)
        lower_text = full_text.lower()

        # ---------------------------------------------------------
        # 1. CLASSIFICATION
        # ---------------------------------------------------------
        service_type, request_type, request_subtype, classification_confidence = (
            self._classify_request(lower_text)
        )

        data.classification.service_type = service_type
        data.classification.request_type = request_type
        data.classification.request_subtype = request_subtype
        data.classification.classification_confidence = classification_confidence

        # ---------------------------------------------------------
        # 2. GENERAL CLIENT INFORMATION
        # ---------------------------------------------------------
        data.general.client_name = self._extract_client_name(full_text)
        data.general.client_reference = self._extract_client_reference(full_text)
        data.general.policy_number = self._extract_policy_number(full_text)
        data.general.investment_account_number = (
            self._extract_investment_account_number(full_text)
        )
        data.general.provider = self._extract_provider(full_text)
        data.general.request_date = self._extract_request_date(full_text)
        data.general.requested_action = self._extract_requested_action(
            full_text,
            request_type,
        )
        data.general.client_request_summary = self._extract_request_summary(
            full_text
        )

        # ---------------------------------------------------------
        # 3. INVESTMENT INFORMATION
        # ---------------------------------------------------------
        data.investment.monthly_investment_amount = (
            self._extract_monthly_investment(full_text)
        )

        data.investment.investment_time_horizon = (
            self._extract_time_horizon(full_text)
        )

        data.investment.investment_goal_name = (
            self._extract_goal_name(full_text)
        )

        data.investment.target_amount = (
            self._extract_target_amount(full_text)
        )

        data.investment.target_date = (
            self._extract_target_date(full_text)
        )

        # ---------------------------------------------------------
        # 4. INSURANCE INFORMATION
        # ---------------------------------------------------------
        data.insurance.insurance_category = (
            self._extract_insurance_category(full_text)
        )

        data.insurance.policy_number = (
            self._extract_policy_number(full_text)
        )

        data.insurance.claim_type = (
            self._extract_claim_type(full_text)
        )

        # ---------------------------------------------------------
        # 5. ACCIDENT / POLICE REPORT INFORMATION
        # ---------------------------------------------------------
        accident = data.accident

        accident.case_number = self._extract_case_number(full_text)
        accident.police_station = self._extract_police_station(full_text)
        accident.officer_name = self._extract_officer_name(full_text)
        accident.incident_date = self._extract_incident_date(full_text)
        accident.incident_time = self._extract_incident_time(full_text)
        accident.incident_location = self._extract_incident_location(full_text)
        accident.incident_description = self._extract_description(full_text)
        accident.damages_summary = self._extract_damages(full_text)
        accident.vehicles_involved = self._extract_vehicles(full_text)
        accident.parties_involved = self._extract_parties(full_text)

        # ---------------------------------------------------------
        # 6. ACCIDENT OVERRIDE
        # ---------------------------------------------------------
        # If the document clearly contains a police/accident report,
        # make sure it is classified as an insurance claim.
        if self._looks_like_accident_report(lower_text):
            if "commercial" in lower_text or any(
                term in lower_text
                for term in [
                    "fleet",
                    "truck",
                    "trailer",
                    "freight",
                    "cargo",
                    "delivery",
                    "logistics",
                    "commercial vehicle",
                ]
            ):
                data.classification.service_type = "commercial_insurance"
            else:
                data.classification.service_type = "personal_insurance"

            data.classification.request_type = "claim"
            data.classification.request_subtype = "accident_claim"
            data.classification.classification_confidence = 0.94

        # ---------------------------------------------------------
        # 7. MISSING INFORMATION
        # ---------------------------------------------------------
        data.general.missing_information = self._find_missing_information(
            data
        )

        return data

    # =============================================================
    # CLASSIFICATION
    # =============================================================

    def _classify_request(self, text: str):
        """
        Determine the Royal Square Financial service and client action.
        """

        # Claims / accidents
        if any(
            term in text
            for term in [
                "claim",
                "accident",
                "collision",
                "crash",
                "police report",
                "cas number",
                "case number",
                "stolen",
                "theft",
                "hijack",
            ]
        ):
            if any(
                term in text
                for term in [
                    "fleet",
                    "truck",
                    "trailer",
                    "freight",
                    "cargo",
                    "delivery",
                    "logistics",
                    "commercial vehicle",
                    "business vehicle",
                ]
            ):
                return (
                    "commercial_insurance",
                    "claim",
                    "commercial_vehicle_claim",
                    0.94,
                )

            return (
                "personal_insurance",
                "claim",
                "accident_claim",
                0.94,
            )

        # Life insurance
        if any(
            term in text
            for term in [
                "life insurance",
                "life cover",
                "life policy",
                "death benefit",
                "life assurance",
            ]
        ):
            if any(
                term in text
                for term in [
                    "quote",
                    "quotation",
                    "price",
                    "premium",
                ]
            ):
                return (
                    "life_insurance",
                    "quote_request",
                    "life_insurance_quote",
                    0.95,
                )

            if any(
                term in text
                for term in [
                    "beneficiary",
                    "beneficiaries",
                    "nominee",
                ]
            ):
                return (
                    "life_insurance",
                    "beneficiary_change",
                    "life_policy_beneficiary_change",
                    0.93,
                )

            if any(
                term in text
                for term in [
                    "change",
                    "update",
                    "amend",
                ]
            ):
                return (
                    "life_insurance",
                    "policy_change",
                    "life_policy_change",
                    0.90,
                )

            return (
                "life_insurance",
                "new_request",
                "life_insurance_request",
                0.90,
            )

        # Funeral insurance
        if any(
            term in text
            for term in [
                "funeral insurance",
                "funeral cover",
                "funeral policy",
                "burial cover",
                "burial policy",
            ]
        ):
            if any(
                term in text
                for term in [
                    "quote",
                    "quotation",
                    "price",
                    "premium",
                ]
            ):
                return (
                    "funeral_insurance",
                    "quote_request",
                    "funeral_insurance_quote",
                    0.95,
                )

            if any(
                term in text
                for term in [
                    "beneficiary",
                    "beneficiaries",
                    "nominee",
                ]
            ):
                return (
                    "funeral_insurance",
                    "beneficiary_change",
                    "funeral_policy_beneficiary_change",
                    0.93,
                )

            return (
                "funeral_insurance",
                "new_request",
                "funeral_insurance_request",
                0.90,
            )

        # Health insurance
        if any(
            term in text
            for term in [
                "health insurance",
                "health cover",
                "medical insurance",
                "medical cover",
                "hospital cover",
            ]
        ):
            if any(
                term in text
                for term in [
                    "claim",
                    "medical claim",
                    "hospital claim",
                ]
            ):
                return (
                    "health_insurance",
                    "claim",
                    "health_insurance_claim",
                    0.94,
                )

            if any(
                term in text
                for term in [
                    "quote",
                    "quotation",
                    "price",
                    "premium",
                ]
            ):
                return (
                    "health_insurance",
                    "quote_request",
                    "health_insurance_quote",
                    0.95,
                )

            return (
                "health_insurance",
                "new_request",
                "health_insurance_request",
                0.90,
            )

        # Commercial insurance
        if any(
            term in text
            for term in [
                "commercial insurance",
                "business insurance",
                "business cover",
                "commercial cover",
                "fleet insurance",
                "fleet cover",
            ]
        ):
            if any(
                term in text
                for term in [
                    "renew",
                    "renewal",
                ]
            ):
                return (
                    "commercial_insurance",
                    "renewal",
                    "commercial_policy_renewal",
                    0.93,
                )

            if any(
                term in text
                for term in [
                    "quote",
                    "quotation",
                    "price",
                    "premium",
                ]
            ):
                return (
                    "commercial_insurance",
                    "quote_request",
                    "commercial_insurance_quote",
                    0.95,
                )

            return (
                "commercial_insurance",
                "new_request",
                "commercial_insurance_request",
                0.90,
            )

        # Personal insurance
        if any(
            term in text
            for term in [
                "personal insurance",
                "personal cover",
                "car insurance",
                "vehicle insurance",
                "motor insurance",
                "motor cover",
                "home insurance",
                "house insurance",
                "property insurance",
            ]
        ):
            if any(
                term in text
                for term in [
                    "quote",
                    "quotation",
                    "price",
                    "premium",
                ]
            ):
                return (
                    "personal_insurance",
                    "quote_request",
                    "personal_insurance_quote",
                    0.95,
                )

            if any(
                term in text
                for term in [
                    "renew",
                    "renewal",
                ]
            ):
                return (
                    "personal_insurance",
                    "renewal",
                    "personal_policy_renewal",
                    0.93,
                )

            return (
                "personal_insurance",
                "new_request",
                "personal_insurance_request",
                0.90,
            )

        # Goal-based investment
        if any(
            term in text
            for term in [
                "financial goal",
                "investment goal",
                "savings goal",
                "saving for",
                "save for",
                "target amount",
                "target date",
                "retirement goal",
                "education goal",
                "house deposit",
                "buy a house",
            ]
        ):
            return (
                "goal_based_investment",
                "new_financial_goal",
                "investment_goal",
                0.94,
            )

        # General investment
        if any(
            term in text
            for term in [
                "investment",
                "invest",
                "unit trust",
                "portfolio",
                "shares",
                "stocks",
                "investment account",
            ]
        ):
            if any(
                term in text
                for term in [
                    "review",
                    "performance",
                    "check my investment",
                ]
            ):
                return (
                    "investment",
                    "investment_review",
                    "portfolio_review",
                    0.92,
                )

            if any(
                term in text
                for term in [
                    "increase",
                    "decrease",
                    "change contribution",
                    "monthly contribution",
                    "contribution",
                ]
            ):
                return (
                    "investment",
                    "contribution_change",
                    "investment_contribution_change",
                    0.91,
                )

            return (
                "investment",
                "investment_request",
                "general_investment_request",
                0.90,
            )

        # Financial planning
        if any(
            term in text
            for term in [
                "financial plan",
                "financial planning",
                "financial planner",
                "financial advice",
                "financial review",
                "financial assessment",
                "retirement planning",
                "estate planning",
                "budget",
            ]
        ):
            if any(
                term in text
                for term in [
                    "review",
                    "review my",
                    "annual review",
                ]
            ):
                return (
                    "financial_planning",
                    "financial_review",
                    "financial_plan_review",
                    0.92,
                )

            return (
                "financial_planning",
                "new_request",
                "financial_planning_request",
                0.90,
            )

        # Status request
        if any(
            term in text
            for term in [
                "status",
                "update on",
                "what is happening with",
                "where is my",
                "progress of",
            ]
        ):
            return (
                "general_service",
                "status_request",
                "request_status",
                0.86,
            )

        # Document request
        if any(
            term in text
            for term in [
                "send me",
                "provide me",
                "need a copy",
                "document",
                "statement",
                "certificate",
            ]
        ):
            return (
                "general_service",
                "document_request",
                "client_document_request",
                0.82,
            )

        return (
            "unknown",
            "other",
            None,
            0.45,
        )

    # =============================================================
    # GENERAL CLIENT DATA
    # =============================================================

    def _extract_client_name(self, text: str) -> Optional[ExtractedField]:
        patterns = [
            r"(?:CLIENT\s*NAME|FULL\s*NAME|NAME)\s*[:\-]\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,4})",
            r"(?:MY\s+NAME\s+IS)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,4})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                return ExtractedField(
                    value=value,
                    confidence=0.92,
                    source_snippet=match.group(0),
                )

        return ExtractedField()

    def _extract_client_reference(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"\b(?:CLIENT\s*(?:REF|REFERENCE)|CUSTOMER\s*(?:REF|REFERENCE))"
            r"\s*[:#\-]?\s*([A-Z0-9\-\/]{3,30})\b",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            return ExtractedField(
                value=match.group(1),
                confidence=0.94,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_policy_number(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"\b(?:POLICY\s*(?:NUMBER|NO\.?|#)|INSURANCE\s*POLICY|POLICY)"
            r"\s*[:\-]?\s*([A-Z0-9\-\/]{4,30})\b",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            value = match.group(1).strip()

            if not any(
                word in value.upper()
                for word in ["NUMBER", "SECTION", "HOLDER", "DETAIL"]
            ):
                return ExtractedField(
                    value=value,
                    confidence=0.96,
                    source_snippet=match.group(0),
                )

        # Common Royal Square-style formats
        format_match = re.search(
            r"\b(?:POL-[A-Z0-9\-]{4,20}|RSF-[A-Z0-9\-]{4,20})\b",
            text,
            re.IGNORECASE,
        )

        if format_match:
            return ExtractedField(
                value=format_match.group(0),
                confidence=0.92,
                source_snippet=format_match.group(0),
            )

        return ExtractedField()

    def _extract_investment_account_number(
        self,
        text: str,
    ) -> ExtractedField:

        pattern = re.compile(
            r"\b(?:INVESTMENT\s*ACCOUNT|ACCOUNT\s*NUMBER|ACCOUNT\s*NO\.?|"
            r"ACCOUNT\s*#)\s*[:\-]?\s*([A-Z0-9\-\/]{4,30})\b",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            return ExtractedField(
                value=match.group(1),
                confidence=0.92,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_provider(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"\b(?:PROVIDER|INSURER|INSURANCE\s*COMPANY|COMPANY)"
            r"\s*[:\-]\s*([A-Za-z0-9&\-\.\s]{3,60})",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            return ExtractedField(
                value=match.group(1).strip(),
                confidence=0.84,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_request_date(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:REQUEST\s*DATE|DATE\s*OF\s*REQUEST|SUBMISSION\s*DATE)"
            r"\s*[:\-]?\s*"
            r"(\d{4}[\-\/]\d{1,2}[\-\/]\d{1,2}|\d{1,2}[\-\/]\d{1,2}[\-\/]\d{4})",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            normalized = self._normalize_date(match.group(1))

            return ExtractedField(
                value=normalized,
                confidence=0.92,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_requested_action(
        self,
        text: str,
        request_type: str,
    ) -> ExtractedField:

        action_map = {
            "new_request": "Start a new service request",
            "claim": "Submit an insurance claim",
            "policy_review": "Review an existing policy",
            "policy_change": "Change an existing policy",
            "quote_request": "Request a quotation",
            "renewal": "Renew an existing policy",
            "document_submission": "Submit documents",
            "document_request": "Request documents",
            "beneficiary_change": "Change beneficiaries",
            "personal_details_change": "Update personal details",
            "investment_request": "Make an investment request",
            "investment_review": "Review investments",
            "financial_review": "Request a financial review",
            "new_financial_goal": "Create a new financial goal",
            "contribution_change": "Change investment contributions",
            "status_request": "Request a status update",
            "general_question": "Ask a general question",
            "other": "General request",
        }

        value = action_map.get(request_type, "General request")

        return ExtractedField(
            value=value,
            confidence=0.80,
            source_snippet=f"Detected request type: {request_type}",
        )

    def _extract_request_summary(self, text: str) -> ExtractedField:
        cleaned = " ".join(text.split())

        if not cleaned:
            return ExtractedField()

        # Keep the local summary short enough for backend storage.
        summary = cleaned[:400]

        return ExtractedField(
            value=summary,
            confidence=0.70,
            source_snippet=summary,
        )

    # =============================================================
    # INVESTMENT DATA
    # =============================================================

    def _extract_monthly_investment(self, text: str) -> ExtractedField:
        patterns = [
            r"(?:MONTHLY\s*(?:INVESTMENT|CONTRIBUTION|SAVING))"
            r"\s*(?:AMOUNT)?\s*[:\-]?\s*(?:R|ZAR)?\s*([\d\s,\.]+)",

            r"(?:INVEST|CONTRIBUTE|SAVE)\s+"
            r"(?:R|ZAR)?\s*([\d\s,\.]+)\s*(?:PER\s+MONTH|MONTHLY)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                amount = self._clean_money(match.group(1))

                return ExtractedField(
                    value=f"R{amount}",
                    confidence=0.91,
                    source_snippet=match.group(0),
                )

        return ExtractedField()

    def _extract_time_horizon(self, text: str) -> ExtractedField:
        patterns = [
            r"(\d{1,3})\s*(?:YEAR|YEARS)\s*(?:HORIZON|INVESTMENT|PLAN)?",
            r"(?:FOR|OVER|WITHIN)\s+(\d{1,3})\s*(?:YEAR|YEARS)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                value = f"{match.group(1)} years"

                return ExtractedField(
                    value=value,
                    confidence=0.88,
                    source_snippet=match.group(0),
                )

        return ExtractedField()

    def _extract_goal_name(self, text: str) -> ExtractedField:
        patterns = [
            r"(?:GOAL|INVESTMENT\s*GOAL)\s*[:\-]\s*([^\r\n\.]{3,100})",
            r"(?:I\s*(?:AM)?\s*SAVING\s+FOR|SAVING\s+FOR)\s+([^\r\n\.]{3,100})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                return ExtractedField(
                    value=match.group(1).strip(),
                    confidence=0.82,
                    source_snippet=match.group(0),
                )

        return ExtractedField()

    def _extract_target_amount(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:TARGET\s*(?:AMOUNT|VALUE)|GOAL\s*(?:AMOUNT|VALUE)|"
            r"WANT\s+TO\s+REACH|NEED)\s*"
            r"[:\-]?\s*(?:R|ZAR)?\s*([\d\s,\.]+)",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            amount = self._clean_money(match.group(1))

            return ExtractedField(
                value=f"R{amount}",
                confidence=0.88,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_target_date(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:TARGET\s*DATE|GOAL\s*DATE|BY)\s*[:\-]?\s*"
            r"(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|\d{4}[\-\/]\d{1,2}[\-\/]\d{1,2})",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            value = match.group(1)

            try:
                value = self._normalize_date(value)
            except Exception:
                pass

            return ExtractedField(
                value=value,
                confidence=0.86,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    # =============================================================
    # INSURANCE DATA
    # =============================================================

    def _extract_insurance_category(self, text: str) -> ExtractedField:
        lower = text.lower()

        if any(
            term in lower
            for term in [
                "life insurance",
                "life cover",
                "life policy",
                "life assurance",
            ]
        ):
            return ExtractedField(
                value="Life Insurance",
                confidence=0.96,
                source_snippet="Detected life insurance terminology",
            )

        if any(
            term in lower
            for term in [
                "funeral insurance",
                "funeral cover",
                "funeral policy",
                "burial cover",
            ]
        ):
            return ExtractedField(
                value="Funeral Insurance",
                confidence=0.96,
                source_snippet="Detected funeral insurance terminology",
            )

        if any(
            term in lower
            for term in [
                "health insurance",
                "health cover",
                "medical insurance",
                "medical cover",
                "hospital cover",
            ]
        ):
            return ExtractedField(
                value="Health Insurance",
                confidence=0.96,
                source_snippet="Detected health insurance terminology",
            )

        if any(
            term in lower
            for term in [
                "commercial insurance",
                "business insurance",
                "commercial cover",
                "fleet insurance",
                "fleet cover",
            ]
        ):
            return ExtractedField(
                value="Commercial Insurance",
                confidence=0.96,
                source_snippet="Detected commercial insurance terminology",
            )

        if any(
            term in lower
            for term in [
                "personal insurance",
                "personal cover",
                "car insurance",
                "vehicle insurance",
                "motor insurance",
                "home insurance",
                "property insurance",
            ]
        ):
            return ExtractedField(
                value="Personal Insurance",
                confidence=0.95,
                source_snippet="Detected personal insurance terminology",
            )

        # Accident fallback
        if self._looks_like_accident_report(lower):
            if any(
                term in lower
                for term in [
                    "fleet",
                    "truck",
                    "trailer",
                    "freight",
                    "cargo",
                    "delivery",
                    "logistics",
                ]
            ):
                return ExtractedField(
                    value="Commercial Insurance",
                    confidence=0.92,
                    source_snippet="Detected commercial vehicle/fleet indicators",
                )

            return ExtractedField(
                value="Personal Insurance",
                confidence=0.90,
                source_snippet="Detected passenger vehicle accident indicators",
            )

        return ExtractedField()

    def _extract_claim_type(self, text: str) -> ExtractedField:
        lower = text.lower()

        if any(
            term in lower
            for term in ["theft", "stolen", "hijack", "hijacked"]
        ):
            return ExtractedField(
                value="Vehicle Theft / Hijacking Claim",
                confidence=0.90,
            )

        if any(
            term in lower
            for term in [
                "towed",
                "write-off",
                "severe damage",
                "non-drivable",
            ]
        ):
            return ExtractedField(
                value="Major Collision",
                confidence=0.88,
            )

        if "rear" in lower and (
            "hit" in lower or "collided" in lower or "collision" in lower
        ):
            return ExtractedField(
                value="Rear-End Collision",
                confidence=0.85,
            )

        if self._looks_like_accident_report(lower):
            return ExtractedField(
                value="Standard Motor Collision Claim",
                confidence=0.80,
            )

        return ExtractedField()

    # =============================================================
    # ACCIDENT DATA
    # =============================================================

    def _extract_case_number(self, text: str) -> ExtractedField:
        cas_specific = re.compile(
            r"\bCAS\s*(?:NO\.?|NUMBER|#)?\s*[:\-]?"
            r"\s*([0-9]{1,6}[\/\-][0-9]{1,4}[\/\-][0-9]{2,4})\b",
            re.IGNORECASE,
        )

        match = cas_specific.search(text)

        if match:
            value = match.group(1).strip()

            return ExtractedField(
                value=f"CAS {value}",
                confidence=0.98,
                source_snippet=match.group(0),
            )

        oar_pattern = re.compile(
            r"\b(?:O\.?A\.?R\.?|ACCIDENT\s*REPORT)"
            r"\s*(?:REF|NO\.?|NUMBER|#)?\s*[:\-]?"
            r"\s*([A-Z0-9]{2,8}[\/\-][A-Z0-9\/\-]+)\b",
            re.IGNORECASE,
        )

        match = oar_pattern.search(text)

        if match:
            return ExtractedField(
                value=match.group(1).strip(),
                confidence=0.92,
                source_snippet=match.group(0),
            )

        general_pattern = re.compile(
            r"\b(?:CASE|CR|DOCKET|OB)\s*(?:NO\.?|NUMBER|#)?"
            r"\s*[:\-]?\s*([A-Z0-9]{1,6}[\/\-][A-Z0-9\/\-]+)\b",
            re.IGNORECASE,
        )

        match = general_pattern.search(text)

        if match:
            value = match.group(1).strip()

            if not any(
                word in value.upper()
                for word in [
                    "REPORT",
                    "DOCKET",
                    "SECTION",
                    "ACCIDENT",
                ]
            ):
                return ExtractedField(
                    value=value,
                    confidence=0.88,
                    source_snippet=match.group(0),
                )

        ref_pattern = re.compile(
            r"\b(?:REF|REFERENCE)\s*(?:NO\.?|#)?"
            r"\s*[:\-]?\s*([A-Z0-9\/\-]{4,20})\b",
            re.IGNORECASE,
        )

        match = ref_pattern.search(text)

        if match:
            value = match.group(1).strip()

            if not any(
                word in value.upper()
                for word in [
                    "REPORT",
                    "DOCKET",
                    "SECTION",
                    "ACCIDENT",
                ]
            ):
                return ExtractedField(
                    value=value,
                    confidence=0.75,
                    source_snippet=match.group(0),
                )

        return ExtractedField()

    def _extract_police_station(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:POLICE\s*STATION|POLISIESTASIE|SAPS\s*STATION|"
            r"PRECINCT|STATION)\s*[:\-]?\s*"
            r"([A-Za-z0-9\s\.\-]{3,35}(?:SAPS|Police\s*Station)?)",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            candidate = match.group(1).strip()

            candidate = re.split(
                r"(?:Date|Case|Officer|Tel|Time)",
                candidate,
                flags=re.IGNORECASE,
            )[0].strip()

            if len(candidate) > 2:
                known = any(
                    station in candidate.lower()
                    for station in KNOWN_STATIONS
                )

                confidence = 0.95 if known else 0.88

                return ExtractedField(
                    value=candidate,
                    confidence=confidence,
                    source_snippet=match.group(0),
                )

        lower_text = text.lower()

        for station in KNOWN_STATIONS:
            if station in lower_text:
                idx = lower_text.find(station)
                actual = text[idx:idx + len(station)]

                formatted = f"{actual.title()} SAPS"

                return ExtractedField(
                    value=formatted,
                    confidence=0.90,
                    source_snippet=text[
                        max(0, idx - 10):idx + len(station) + 10
                    ],
                )

        return ExtractedField()

    def _extract_officer_name(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:INVESTIGATING\s*OFFICER|REPORTING\s*OFFICER|"
            r"ATTENDING\s*OFFICER|COMPLETED\s*BY|OFFICER\s*NAME|OFFICER)"
            r"\s*[:\-]\s*"
            r"((?:CONSTABLE|CST|SERGEANT|SGT|INSPECTOR|INSP|"
            r"WARRANT\s*OFFICER|W\/O|CAPTAIN|CAPT|DETECTIVE|DET|"
            r"COLONEL|COL)?\.?\s*[A-Za-z\s\.\-]{3,35})",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            value = match.group(1).strip()

            value = re.split(
                r"(?:Badge|Date|Station|Rank|Force|\()",
                value,
                flags=re.IGNORECASE,
            )[0].strip()

            if len(value) >= 3:
                return ExtractedField(
                    value=value,
                    confidence=0.92,
                    source_snippet=match.group(0),
                )

        rank_pattern = re.compile(
            r"\b(Constable|Cst\.|Sergeant|Sgt\.|Inspector|Insp\.|"
            r"Warrant\s*Officer|W\/O|Captain|Capt\.)\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            re.IGNORECASE,
        )

        match = rank_pattern.search(text)

        if match:
            full_name = (
                f"{match.group(1).title()} "
                f"{match.group(2).title()}"
            )

            return ExtractedField(
                value=full_name,
                confidence=0.90,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_incident_date(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:DATE\s*OF\s*ACCIDENT|INCIDENT\s*DATE|"
            r"DATE\s*OF\s*INCIDENT|ACCIDENT\s*DATE|DATE)"
            r"\s*[:\-]?\s*"
            r"(\d{1,4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,4}|"
            r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            normalized = self._normalize_date(match.group(1))

            return ExtractedField(
                value=normalized,
                confidence=0.94,
                source_snippet=match.group(0),
            )

        generic_date = re.compile(
            r"\b(\d{4}[\-\/]\d{2}[\-\/]\d{2}|"
            r"\d{2}[\-\/]\d{2}[\-\/]\d{4})\b"
        )

        match = generic_date.search(text)

        if match:
            normalized = self._normalize_date(match.group(1))

            return ExtractedField(
                value=normalized,
                confidence=0.80,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _normalize_date(self, raw: str) -> str:
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d %b %Y",
            "%d %B %Y",
            "%Y.%m.%d",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(raw.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return raw

    def _extract_incident_time(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:TIME\s*OF\s*ACCIDENT|INCIDENT\s*TIME|TIME)"
            r"\s*[:\-]?\s*"
            r"(\d{1,2}[:hH]\d{2}(?:\s*[AaPp][Mm])?)",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            value = (
                match.group(1)
                .replace("h", ":")
                .replace("H", ":")
                .strip()
            )

            return ExtractedField(
                value=value,
                confidence=0.90,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_incident_location(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:(?:ACCIDENT\s*SCENE\s*\/)?\s*"
            r"(?:LOCATION|PLACE\s*OF\s*ACCIDENT|"
            r"SCENE\s*OF\s*ACCIDENT|ACCIDENT\s*SCENE))"
            r"\s*[:\-]?\s*([^\r\n]{5,80})",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            value = match.group(1).strip()

            value = re.sub(
                r"^(?:\/\s*LOCATION\s*[:\-]?)?\s*",
                "",
                value,
                flags=re.IGNORECASE,
            )

            value = value.split("  ")[0].strip()

            return ExtractedField(
                value=value,
                confidence=0.88,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_description(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:DESCRIPTION\s*OF\s*ACCIDENT|BRIEF\s*DESCRIPTION|"
            r"SKETCH\s*AND\s*DESCRIPTION|DETAILS|NARRATIVE)"
            r"\s*[:\-]?\s*([^\r\n]{15,250})",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            return ExtractedField(
                value=match.group(1).strip(),
                confidence=0.82,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_damages(self, text: str) -> ExtractedField:
        pattern = re.compile(
            r"(?:DAMAGE(?:S)?\s*TO\s*VEHICLE|"
            r"EXTENT\s*OF\s*DAMAGE|DAMAGES)"
            r"\s*[:\-]?\s*([^\r\n]{5,150})",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if match:
            return ExtractedField(
                value=match.group(1).strip(),
                confidence=0.85,
                source_snippet=match.group(0),
            )

        return ExtractedField()

    def _extract_vehicles(self, text: str) -> List[ExtractedVehicle]:
        vehicles = []

        reg_pattern = re.compile(
            r"\b([A-Z]{2,3}\s*\d{2,4}\s*[A-Z]{0,2}\s*"
            r"(?:GP|ZN|WP|EC|FS|MP|NW|NC|L)?)\b"
        )

        reg_matches = reg_pattern.findall(text)

        lower_text = text.lower()

        found_makes = [
            make.title()
            for make in COMMON_VEHICLE_MAKES
            if f" {make} " in f" {lower_text} "
        ]

        if found_makes or reg_matches:
            count = max(
                len(found_makes),
                len(reg_matches),
                1,
            )

            for i in range(min(count, 3)):
                make = (
                    found_makes[i]
                    if i < len(found_makes)
                    else None
                )

                registration = (
                    reg_matches[i]
                    if i < len(reg_matches)
                    else None
                )

                vehicles.append(
                    ExtractedVehicle(
                        make_model=make,
                        registration_number=registration,
                        confidence=(
                            0.85
                            if make and registration
                            else 0.75
                        ),
                    )
                )

        return vehicles

    def _extract_parties(self, text: str) -> List[ExtractedParty]:
        parties = []

        patterns = [
            (
                r"(?:DRIVER|DRIVER NAME)\s*[:\-]\s*"
                r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})",
                "Driver",
            ),
            (
                r"(?:PASSENGER|PASSENGER NAME)\s*[:\-]\s*"
                r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})",
                "Passenger",
            ),
            (
                r"(?:WITNESS|WITNESS NAME)\s*[:\-]\s*"
                r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})",
                "Witness",
            ),
            (
                r"(?:PEDESTRIAN|PEDESTRIAN NAME)\s*[:\-]\s*"
                r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})",
                "Pedestrian",
            ),
        ]

        for pattern, role in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                parties.append(
                    ExtractedParty(
                        full_name=match.group(1).strip(),
                        role=role,
                        confidence=0.88,
                    )
                )

        return parties

    # =============================================================
    # HELPERS
    # =============================================================

    def _looks_like_accident_report(self, text: str) -> bool:
        indicators = [
            "cas ",
            "police station",
            "saps",
            "accident report",
            "accident scene",
            "collision",
            "vehicle accident",
            "motor accident",
            "incident report",
        ]

        matches = sum(
            1 for indicator in indicators
            if indicator in text
        )

        return matches >= 2

    def _find_missing_information(
        self,
        data: ExtractionData,
    ) -> List[str]:

        missing = []

        service = data.classification.service_type
        request = data.classification.request_type

        # General information
        if not data.general.client_name.value:
            missing.append("client_name")

        # Insurance requests
        if service in {
            "life_insurance",
            "funeral_insurance",
            "health_insurance",
            "personal_insurance",
            "commercial_insurance",
        }:
            if request not in {"claim", "document_request"}:
                if not data.insurance.insurance_category.value:
                    missing.append("insurance_category")

        # Claims
        if request == "claim":
            if not data.general.policy_number.value:
                missing.append("policy_number")

        # Investment / goals
        if service in {
            "investment",
            "goal_based_investment",
        }:
            if not data.investment.target_amount.value:
                missing.append("target_amount")

            if not data.investment.investment_time_horizon.value:
                missing.append("investment_time_horizon")

        # Accident reports
        if self._has_accident_data(data):
            if not data.accident.case_number.value:
                missing.append("case_number")

            if not data.accident.incident_date.value:
                missing.append("incident_date")

        return missing

    def _has_accident_data(self, data: ExtractionData) -> bool:
        accident = data.accident

        return any(
            [
                accident.case_number.value,
                accident.police_station.value,
                accident.officer_name.value,
                accident.incident_date.value,
                accident.incident_location.value,
                accident.incident_description.value,
                len(accident.vehicles_involved) > 0,
                len(accident.parties_involved) > 0,
            ]
        )

    def _clean_money(self, value: str) -> str:
        cleaned = value.strip()

        # Remove spaces used as thousands separators.
        cleaned = cleaned.replace(" ", "")

        # Preserve decimal point but remove commas.
        cleaned = cleaned.replace(",", "")

        return cleaned