from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.case import Case, CaseRequirement
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