from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AIIngestRequest(BaseModel):
    case_id: str
    document_id: Optional[str] = None
    doc_type_detected: Optional[str] = None

    overall_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    extracted_fields: Dict[str, str] = Field(
        default_factory=dict,
    )

    field_confidences: Dict[str, float] = Field(
        default_factory=dict,
    )

    flagged_anomalies: List[str] = Field(
        default_factory=list,
    )


class AIIngestResponse(BaseModel):
    case_id: str
    current_stage: str
    status: str
    overall_confidence: Optional[float]
    intervention_required: bool
    trigger_reason: Optional[str] = None