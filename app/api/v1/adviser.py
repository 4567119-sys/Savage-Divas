from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.case import (
    AdviserInterventionContext,
    Case,
    Notification,
)
from app.models.client import Client
from app.schemas.adviser import (
    AdviserContextResponse,
    AdviserOverrideRequest,
)

router = APIRouter(prefix="/adviser", tags=["Adviser"])


@router.get("/cases")
def get_adviser_cases(
    db: Session = Depends(get_db),
):
    cases = (
        db.query(Case)
        .filter(
            Case.status.in_(
                [
                    "ADVISER_INTERVENTION",
                    "ACTION_REQUIRED",
                ]
            )
        )
        .order_by(Case.updated_at.desc())
        .all()
    )

    return [
        {
            "case_id": case.id,
            "client_id": case.client_id,
            "adviser_id": case.adviser_id,
            "case_type": case.case_type,
            "title": case.title,
            "current_stage": case.current_stage,
            "status": case.status,
            "overall_confidence": case.overall_confidence,
            "updated_at": case.updated_at,
        }
        for case in cases
    ]


@router.get(
    "/cases/{case_id}/context",
    response_model=AdviserContextResponse,
)
def get_adviser_context(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    context = (
        db.query(AdviserInterventionContext)
        .filter(
            AdviserInterventionContext.case_id == case_id
        )
        .first()
    )

    if not context:
        raise HTTPException(
            status_code=404,
            detail="No adviser intervention context found.",
        )

    client = db.get(Client, case.client_id)

    missing_requirements = [
        requirement.title
        for requirement in case.requirements
        if not requirement.is_fulfilled
    ]

    uploaded_documents = [
        document.filename
        for document in case.documents
    ]

    if case.overall_confidence is not None:
        confidence_text = (
            f"{case.overall_confidence:.0%}"
        )
    else:
        confidence_text = "Not available"

    automation_summary = (
        f"Case '{case.title}' was processed by the automated "
        f"workflow. The current AI confidence is {confidence_text}. "
        f"The case is currently at {case.current_stage}."
    )

    if uploaded_documents:
        automation_summary += (
            f" Documents received: "
            f"{', '.join(uploaded_documents)}."
        )
    else:
        automation_summary += " No documents have been recorded yet."

    unresolved_parts = []

    if missing_requirements:
        unresolved_parts.append(
            "Missing requirements: "
            + ", ".join(missing_requirements)
        )

    if context.trigger_reason:
        unresolved_parts.append(
            "Intervention reason: "
            + context.trigger_reason.replace("_", " ").title()
        )

    unresolved_issues = (
        "; ".join(unresolved_parts)
        if unresolved_parts
        else context.unresolved_issues
    )

    client_snapshot_parts = []

    if client:
        client_snapshot_parts.append(
            f"Client: {client.full_name}"
        )

        if client.preferred_language:
            client_snapshot_parts.append(
                f"Preferred language: {client.preferred_language}"
            )

        if client.accessibility_mode:
            client_snapshot_parts.append(
                "Accessibility mode: enabled"
            )

        if client.monthly_income is not None:
            client_snapshot_parts.append(
                f"Monthly income: R{client.monthly_income:,.2f}"
            )

        if client.total_net_worth is not None:
            client_snapshot_parts.append(
                f"Total net worth: R{client.total_net_worth:,.2f}"
            )

    client_snapshot_parts.append(
        f"Case type: {case.case_type}"
    )
    client_snapshot_parts.append(
        f"Case stage: {case.current_stage}"
    )

    client_story_snapshot = ". ".join(
        client_snapshot_parts
    ) + "."

    return AdviserContextResponse(
        case_id=context.case_id,
        trigger_reason=context.trigger_reason,
        automation_summary=automation_summary,
        unresolved_issues=unresolved_issues,
        client_story_snapshot=client_story_snapshot,
        adviser_notes=context.adviser_notes,
        is_resolved=context.is_resolved,
        created_at=context.created_at,
        resolved_at=context.resolved_at,
    )


@router.post("/cases/{case_id}/override")
def adviser_override(
    case_id: str,
    decision: AdviserOverrideRequest,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    if decision.decision not in {
        "APPROVE",
        "REJECT",
        "REQUEST_INFORMATION",
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid adviser decision.",
        )

    if decision.decision == "APPROVE":
        case.current_stage = "APPROVED"
        case.status = "APPROVED"

    elif decision.decision == "REJECT":
        case.current_stage = "REJECTED"
        case.status = "REJECTED"

    else:
        case.current_stage = "ADVISER_REVIEW"
        case.status = "ACTION_REQUIRED"

        notification = Notification(
            id=str(uuid4()),
            client_id=case.client_id,
            case_id=case.id,
            title="Additional information required",
            message=(
                decision.adviser_notes
                or "Your adviser has requested additional information for this case."
            ),
            is_read=False,
        )

        db.add(notification)

    context = (
        db.query(AdviserInterventionContext)
        .filter(
            AdviserInterventionContext.case_id == case_id
        )
        .first()
    )

    if context:
        context.adviser_notes = decision.adviser_notes
        context.is_resolved = decision.decision in {
            "APPROVE",
            "REJECT",
        }

    db.commit()

    return {
        "case_id": case.id,
        "decision": decision.decision,
        "current_stage": case.current_stage,
        "status": case.status,
    }