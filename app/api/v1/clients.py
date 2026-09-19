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