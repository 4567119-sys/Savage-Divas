from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    client_id: str
    case_type: str
    title: str
    adviser_id: Optional[str] = None


class CaseResponse(BaseModel):
    id: str
    client_id: str
    adviser_id: Optional[str] = None
    case_type: str
    title: str
    current_stage: str
    status: str
    overall_confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseProgressResponse(BaseModel):
    case_id: str
    current_stage: str
    status: str
    overall_confidence: Optional[float] = None
    completed_requirements: int
    total_requirements: int
    documents_uploaded: int
    intervention_required: bool


class CaseRequirementCreate(BaseModel):
    title: str
    requirement_type: str = "DOCUMENT"