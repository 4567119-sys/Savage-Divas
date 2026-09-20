from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientResponse


router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/", response_model=ClientResponse)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
):
    existing_client = (
        db.query(Client)
        .filter(Client.email == client_data.email)
        .first()
    )

    if existing_client:
        raise HTTPException(
            status_code=400,
            detail="A client with this email already exists.",
        )

    client = Client(
        id=str(uuid4()),
        **client_data.model_dump(),
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: str,
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found.",
        )

    return client


@router.get("/{client_id}/dashboard")
def get_client_dashboard(
    client_id: str,
    db: Session = Depends(get_db),
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found.",
        )

    active_case = None
    if client.cases:
        active_case = max(
            client.cases,
            key=lambda case: case.updated_at,
        )

        if active_case.status in {"CLOSED", "CANCELLED", "ARCHIVED"}:
            active_case = next(
                (
                    case
                    for case in sorted(
                        client.cases,
                        key=lambda case: case.updated_at,
                        reverse=True,
                    )
                    if case.status not in {"CLOSED", "CANCELLED", "ARCHIVED"}
                ),
                active_case,
            )

    requirements = active_case.requirements if active_case else []
    total_requirements = len(requirements)
    fulfilled_requirements = sum(
        1 for requirement in requirements if requirement.is_fulfilled
    )
    workflow_progress_percentage = (
        round((fulfilled_requirements / total_requirements) * 100, 2)
        if total_requirements
        else 0
    )

    outstanding_requirements = [
        {
            "id": requirement.id,
            "title": requirement.title,
            "type": requirement.requirement_type,
            "is_fulfilled": requirement.is_fulfilled,
        }
        for requirement in requirements
        if not requirement.is_fulfilled
    ]

    financial_goals = []
    for goal in client.goals:
        target_amount = goal.target_amount or 0
        current_amount = goal.current_amount or 0
        progress = (
            round((current_amount / target_amount) * 100, 2)
            if target_amount
            else (100 if current_amount > 0 else 0)
        )

        financial_goals.append(
            {
                "id": goal.id,
                "title": goal.title,
                "category": goal.category,
                "target_amount": target_amount,
                "current_amount": current_amount,
                "progress_percentage": progress,
                "status": goal.status,
            }
        )

    today = date.today()
    upcoming_life_events = [
        {
            "id": life_event.id,
            "title": life_event.title,
            "event_date": life_event.event_date.isoformat()
            if life_event.event_date
            else None,
            "financial_impact": life_event.financial_impact,
        }
        for life_event in sorted(
            client.life_events,
            key=lambda item: item.event_date or date.max,
        )
        if life_event.event_date and life_event.event_date >= today
    ]

    unread_notifications = [
        {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "created_at": notification.created_at.isoformat(),
        }
        for notification in client.notifications
        if not notification.is_read
    ]

    return {
        "client_name": client.full_name,
        "preferred_language": client.preferred_language,
        "accessibility_mode": client.accessibility_mode,
        "active_case": active_case.title if active_case else None,
        "case_current_stage": active_case.current_stage if active_case else None,
        "case_status": active_case.status if active_case else None,
        "workflow_progress_percentage": workflow_progress_percentage,
        "outstanding_requirements": outstanding_requirements,
        "financial_goals": financial_goals,
        "upcoming_life_events": upcoming_life_events,
        "unread_notifications": unread_notifications,
    }