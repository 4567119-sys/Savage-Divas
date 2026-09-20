from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    value: Optional[str] = Field(
        None,
        description="Extracted value or null if not detected"
    )
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    source_snippet: Optional[str] = Field(
        None,
        description="Text snippet or evidence from the source"
    )


class ExtractedVehicle(BaseModel):
    make_model: Optional[str] = None
    registration_number: Optional[str] = None
    driver_name: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class ExtractedParty(BaseModel):
    full_name: Optional[str] = None
    id_or_license: Optional[str] = None
    contact_number: Optional[str] = None
    role: Optional[str] = Field(
        None,
        description="e.g. Driver, Passenger, Pedestrian, Witness"
    )
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class AccidentReportData(BaseModel):
    """
    Existing accident/claim extraction fields.
    These are preserved for backward compatibility.
    """

    case_number: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Police CAS No, Accident Report (OAR) number, or reference number"
    )

    police_station: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Name of the reporting police station"
    )

    officer_name: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Name and/or rank of reporting or investigating officer"
    )

    incident_date: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Date the incident occurred"
    )

    incident_time: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Time the accident occurred"
    )

    incident_location: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Street, intersection, or physical location"
    )

    incident_description: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Brief description of how the accident occurred"
    )

    damages_summary: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Noted vehicle or property damage"
    )

    vehicles_involved: List[ExtractedVehicle] = Field(
        default_factory=list
    )

    parties_involved: List[ExtractedParty] = Field(
        default_factory=list
    )


class RoyalSquareClassification(BaseModel):
    """
    General Royal Square Financial service classification.
    """

    service_type: str = Field(
        "unknown",
        description=(
            "Royal Square service area: financial_planning, "
            "life_insurance, funeral_insurance, health_insurance, "
            "personal_insurance, commercial_insurance, "
            "goal_based_investment, investment, general_service, unknown"
        )
    )

    request_type: str = Field(
        "other",
        description="Type of client request"
    )

    request_subtype: Optional[str] = Field(
        None,
        description="More specific request classification"
    )

    classification_confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0
    )


class GeneralClientData(BaseModel):
    """
    Information that can apply across different Royal Square services.
    """

    client_name: Optional[ExtractedField] = None

    client_reference: Optional[ExtractedField] = None

    policy_number: Optional[ExtractedField] = None

    investment_account_number: Optional[ExtractedField] = None

    provider: Optional[ExtractedField] = None

    request_date: Optional[ExtractedField] = None

    requested_action: Optional[ExtractedField] = None

    client_request_summary: Optional[ExtractedField] = None

    missing_information: List[str] = Field(
        default_factory=list
    )


class InvestmentData(BaseModel):
    """
    Optional investment/goal information.
    """

    monthly_investment_amount: Optional[ExtractedField] = None

    investment_time_horizon: Optional[ExtractedField] = None

    investment_goal_name: Optional[ExtractedField] = None

    target_amount: Optional[ExtractedField] = None

    target_date: Optional[ExtractedField] = None


class InsuranceData(BaseModel):
    """
    Optional insurance information.
    """

    insurance_category: Optional[ExtractedField] = None

    policy_number: Optional[ExtractedField] = None

    claim_type: Optional[ExtractedField] = None


class ExtractionData(BaseModel):
    """
    Combined response data.

    Accident fields remain available.
    General Royal Square fields support all other services.
    """

    classification: RoyalSquareClassification = Field(
        default_factory=RoyalSquareClassification
    )

    general: GeneralClientData = Field(
        default_factory=GeneralClientData
    )

    investment: InvestmentData = Field(
        default_factory=InvestmentData
    )

    insurance: InsuranceData = Field(
        default_factory=InsuranceData
    )

    accident: AccidentReportData = Field(
        default_factory=AccidentReportData
    )

    additional_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible service-specific fields"
    )


class ProcessingMetadata(BaseModel):
    filename: str
    file_size_bytes: int
    content_type: str
    pages_processed: int = 1
    processing_time_ms: int
    extraction_engine: str
    used_fallback: bool = False

    document_type_detected: str = Field(
        "unknown",
        description=(
            "Detected document type, for example "
            "accident_police_report, insurance_document, "
            "investment_request, financial_planning_request, "
            "client_request, or unknown"
        )
    )


class ExtractionResponse(BaseModel):
    success: bool = True

    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )

    data: ExtractionData

    raw_text_excerpt: Optional[str] = None

    warnings: List[str] = Field(
        default_factory=list
    )

    metadata: ProcessingMetadata


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    gemini_configured: bool
    gemini_model: str
    local_fallback_enabled: bool
