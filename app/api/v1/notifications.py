from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.case import Notification

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("/{client_id}")
def get_client_notifications(
    client_id: str,
    db: Session = Depends(get_db),
):
    notifications = (
        db.query(Notification)
        .filter(Notification.client_id == client_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return notifications