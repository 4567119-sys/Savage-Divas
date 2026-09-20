from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    case_id: Mapped[str] = mapped_column(
        ForeignKey("cases.id"),
        nullable=False,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    storage_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    upload_source: Mapped[str] = mapped_column(
        String(50),
        default="CLIENT",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="UPLOADED",
        nullable=False,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    case: Mapped["Case"] = relationship(
        back_populates="documents",
    )