from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.case import Case
from app.models.document import Document

router = APIRouter(prefix="/cases", tags=["Documents"])


@router.post("/{case_id}/documents")
def upload_document(
    case_id: str,
    filename: str,
    file_type: str | None = None,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    document = Document(
        id=str(uuid4()),
        case_id=case_id,
        filename=filename,
        file_type=file_type,
        status="UPLOADED",
    )

    db.add(document)

    if case.current_stage == "INTAKE":
        case.current_stage = "DOCUMENT_SUBMISSION"

    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "case_id": document.case_id,
        "filename": document.filename,
        "status": document.status,
    }