from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.engine.workflow_engine import determine_next_stage
from app.models.case import (
    AIExtractionLog,
    AdviserInterventionContext,
    Case,
)
from app.models.document import Document
from app.schemas.ai_ingest import AIIngestRequest, AIIngestResponse


router = APIRouter(prefix="/ai", tags=["AI Processing"])


@router.post("/ingest", response_model=AIIngestResponse)
def ingest_ai_result(
    payload: AIIngestRequest,
    db: Session = Depends(get_db),
):
    case = db.get(Case, payload.case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    if payload.document_id:
        document = db.get(Document, payload.document_id)

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        document.status = "PROCESSED"

    log = AIExtractionLog(
        id=str(uuid4()),
        case_id=payload.case_id,
        document_id=payload.document_id,
        doc_type_detected=payload.doc_type_detected,
        overall_confidence=payload.overall_confidence,
        extracted_fields=str(payload.extracted_fields),
        field_confidences=str(payload.field_confidences),
        flagged_anomalies=str(payload.flagged_anomalies),
    )

    next_stage, status, trigger_reason = determine_next_stage(
        case=case,
        confidence=payload.overall_confidence,
        flagged_anomalies=payload.flagged_anomalies,
    )

    case.current_stage = next_stage
    case.status = status
    case.overall_confidence = payload.overall_confidence

    if trigger_reason:
        context = (
            db.query(AdviserInterventionContext)
            .filter(
                AdviserInterventionContext.case_id == case.id
            )
            .first()
        )

        automation_summary = (
            f"AI processing completed with an overall confidence "
            f"score of {payload.overall_confidence:.0%}."
        )

        unresolved_issues = (
            "AI processing requires adviser review because: "
            f"{trigger_reason.replace('_', ' ').lower()}."
        )

        client_story_snapshot = (
            f"Case: {case.title}. "
            f"Case type: {case.case_type}. "
            f"Current workflow stage: {case.current_stage}."
        )

        if context:
            context.trigger_reason = trigger_reason
            context.automation_summary = automation_summary
            context.unresolved_issues = unresolved_issues
            context.client_story_snapshot = client_story_snapshot
            context.is_resolved = False
            context.resolved_at = None

        else:
            intervention_context = AdviserInterventionContext(
                id=str(uuid4()),
                case_id=case.id,
                trigger_reason=trigger_reason,
                automation_summary=automation_summary,
                unresolved_issues=unresolved_issues,
                client_story_snapshot=client_story_snapshot,
                is_resolved=False,
            )

            db.add(intervention_context)

    db.add(log)
    db.commit()

    return AIIngestResponse(
        case_id=case.id,
        current_stage=case.current_stage,
        status=case.status,
        overall_confidence=case.overall_confidence,
        intervention_required=(
            case.status == "ADVISER_INTERVENTION"
        ),
        trigger_reason=trigger_reason,
    )