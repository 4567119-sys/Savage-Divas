from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AdviserOverrideRequest(BaseModel):
    decision: str
    adviser_notes: Optional[str] = None


class AdviserContextResponse(BaseModel):
    case_id: str
    trigger_reason: str
    automation_summary: str
    unresolved_issues: Optional[str] = None
    client_story_snapshot: Optional[str] = None
    adviser_notes: Optional[str] = None
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None