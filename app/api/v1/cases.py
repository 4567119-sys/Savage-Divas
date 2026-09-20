from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.case import (
    AIExtractionLog,
    AdviserInterventionContext,
    Case,
    CaseRequirement,
)
from app.models.client import Client
from app.schemas.case import (
    CaseCreate,
    CaseProgressResponse,
    CaseRequirementCreate,
    CaseResponse,
)

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=CaseResponse)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
):
    client = db.get(Client, case_data.client_id)

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found.",
        )

    case = Case(
        id=str(uuid4()),
        **case_data.model_dump(),
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


@router.post(
    "/{case_id}/requirements",
)
def create_case_requirement(
    case_id: str,
    requirement_data: CaseRequirementCreate,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    requirement = CaseRequirement(
        id=str(uuid4()),
        case_id=case.id,
        title=requirement_data.title,
        requirement_type=requirement_data.requirement_type,
        is_fulfilled=False,
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    return {
        "id": requirement.id,
        "case_id": requirement.case_id,
        "title": requirement.title,
        "requirement_type": requirement.requirement_type,
        "is_fulfilled": requirement.is_fulfilled,
    }


@router.get(
    "/{case_id}/requirements",
)
def get_case_requirements(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    return [
        {
            "id": requirement.id,
            "case_id": requirement.case_id,
            "title": requirement.title,
            "requirement_type": requirement.requirement_type,
            "is_fulfilled": requirement.is_fulfilled,
            "fulfillment_doc_id": requirement.fulfillment_doc_id,
            "rejection_reason": requirement.rejection_reason,
        }
        for requirement in case.requirements
    ]


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    return case


@router.get(
    "/{case_id}/progress",
    response_model=CaseProgressResponse,
)
def get_case_progress(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    total_requirements = len(case.requirements)

    completed_requirements = sum(
        1
        for requirement in case.requirements
        if requirement.is_fulfilled
    )

    return CaseProgressResponse(
        case_id=case.id,
        current_stage=case.current_stage,
        status=case.status,
        overall_confidence=case.overall_confidence,
        completed_requirements=completed_requirements,
        total_requirements=total_requirements,
        documents_uploaded=len(case.documents),
        intervention_required=(
            case.status == "ADVISER_INTERVENTION"
        ),
    )

    total_requirements = len(case.requirements)
    completed_requirements = sum(
        1
        for requirement in case.requirements
        if requirement.is_fulfilled
    )

    return CaseProgressResponse(
        case_id=case.id,
        current_stage=case.current_stage,
        status=case.status,
        overall_confidence=case.overall_confidence,
        completed_requirements=completed_requirements,
        total_requirements=total_requirements,
        documents_uploaded=len(case.documents),
        intervention_required=(
            case.status == "ADVISER_INTERVENTION"
        ),
    )


@router.get("/{case_id}/workflow")
def get_case_workflow_status(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    total_requirements = len(case.requirements)
    fulfilled_requirements = sum(
        1
        for requirement in case.requirements
        if requirement.is_fulfilled
    )
    outstanding_requirements = [
        {
            "id": requirement.id,
            "title": requirement.title,
            "requirement_type": requirement.requirement_type,
            "is_fulfilled": requirement.is_fulfilled,
        }
        for requirement in case.requirements
        if not requirement.is_fulfilled
    ]
    progress_percentage = (
        round((fulfilled_requirements / total_requirements) * 100, 2)
        if total_requirements
        else 0
    )

    latest_ai_log = (
        db.query(AIExtractionLog)
        .filter(AIExtractionLog.case_id == case_id)
        .order_by(AIExtractionLog.created_at.desc())
        .first()
    )

    intervention_context = (
        db.query(AdviserInterventionContext)
        .filter(AdviserInterventionContext.case_id == case_id)
        .first()
    )

    intervention_required = case.status == "ADVISER_INTERVENTION"
    intervention_trigger_reason = (
        intervention_context.trigger_reason
        if intervention_context
        else None
    )
    automation_summary = (
        intervention_context.automation_summary
        if intervention_context
        else (
            f"AI processing completed with overall confidence of "
            f"{case.overall_confidence:.0%}"
            if case.overall_confidence is not None
            else "AI processing has not completed yet."
        )
    )
    unresolved_issues = (
        intervention_context.unresolved_issues
        if intervention_context
        else None
    )
    adviser_review_required = (
        case.current_stage == "ADVISER_REVIEW"
        or intervention_required
        or bool(intervention_context)
    )

    if case.status == "APPROVED":
        next_action = "APPROVED"
    elif case.status == "REJECTED":
        next_action = "REJECTED"
    elif case.status == "ACTION_REQUIRED":
        next_action = "ACTION_REQUIRED"
    elif intervention_required or adviser_review_required:
        next_action = "ADVISER_REVIEW"
    elif total_requirements and fulfilled_requirements < total_requirements:
        next_action = "SUBMIT_REQUIREMENTS"
    elif len(case.documents) == 0:
        next_action = "UPLOAD_DOCUMENTS"
    elif case.overall_confidence is None and latest_ai_log is None:
        next_action = "AI_PROCESSING"
    elif fulfilled_requirements == total_requirements:
        next_action = "COMPLETE"
    else:
        next_action = "AI_PROCESSING"

    return {
        "case_id": case.id,
        "case_title": case.title,
        "case_status": case.status,
        "current_stage": case.current_stage,
        "overall_confidence": case.overall_confidence,
        "progress_percentage": progress_percentage,
        "total_requirements": total_requirements,
        "fulfilled_requirements": fulfilled_requirements,
        "outstanding_requirements": outstanding_requirements,
        "intervention_required": intervention_required,
        "intervention_trigger_reason": intervention_trigger_reason,
        "automation_summary": automation_summary,
        "unresolved_issues": unresolved_issues,
        "next_action": next_action,
        "adviser_review_required": adviser_review_required,
    }