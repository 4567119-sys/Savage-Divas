from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.case import Case
from app.models.document import Document

router = APIRouter(prefix="/cases", tags=["Documents"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/{case_id}/documents")
def upload_document(
    case_id: str,
    file: UploadFile = File(...),
    file_type: str | None = Form(None),
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    document_id = str(uuid4())
    safe_name = Path(file.filename or "document").name
    stored_name = f"{document_id}_{safe_name}"
    storage_path = UPLOAD_DIR / stored_name
    with storage_path.open("wb") as destination:
        destination.write(file.file.read())

    document = Document(
        id=document_id,
        case_id=case_id,
        filename=safe_name,
        file_type=file_type or file.content_type,
        storage_path=str(storage_path),
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
        "storage_path": document.storage_path,
    }
