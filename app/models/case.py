from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )

    adviser_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("advisers.id"),
        nullable=True,
    )

    case_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    current_stage: Mapped[str] = mapped_column(
        String(50),
        default="INTAKE",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="IN_PROGRESS",
        nullable=False,
    )

    overall_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    client: Mapped["Client"] = relationship(
        back_populates="cases",
    )

    adviser: Mapped[Optional["Adviser"]] = relationship(
        back_populates="cases",
    )

    requirements: Mapped[List["CaseRequirement"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    documents: Mapped[List["Document"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    ai_logs: Mapped[List["AIExtractionLog"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    intervention_context: Mapped[Optional["AdviserInterventionContext"]] = (
        relationship(
            back_populates="case",
            uselist=False,
            cascade="all, delete-orphan",
        )
    )

    audit_logs: Mapped[List["AuditLog"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )


class CaseRequirement(Base):
    __tablename__ = "case_requirements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    case_id: Mapped[str] = mapped_column(
        ForeignKey("cases.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    requirement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_fulfilled: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    fulfillment_doc_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("documents.id"),
        nullable=True,
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    case: Mapped["Case"] = relationship(
        back_populates="requirements",
    )


class AIExtractionLog(Base):
    __tablename__ = "ai_extraction_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    case_id: Mapped[str] = mapped_column(
        ForeignKey("cases.id"),
        nullable=False,
    )

    document_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("documents.id"),
        nullable=True,
    )

    doc_type_detected: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    overall_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    extracted_fields: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    field_confidences: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    flagged_anomalies: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    case: Mapped["Case"] = relationship(
        back_populates="ai_logs",
    )


class AdviserInterventionContext(Base):
    __tablename__ = "adviser_intervention_contexts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    case_id: Mapped[str] = mapped_column(
        ForeignKey("cases.id"),
        unique=True,
        nullable=False,
    )

    trigger_reason: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    automation_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    unresolved_issues: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    client_story_snapshot: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    adviser_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_resolved: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    case: Mapped["Case"] = relationship(
        back_populates="intervention_context",
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    case_id: Mapped[str] = mapped_column(
        ForeignKey("cases.id"),
        nullable=False,
    )

    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    case: Mapped["Case"] = relationship(
        back_populates="audit_logs",
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )

    case_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("cases.id"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    client: Mapped["Client"] = relationship(
        back_populates="notifications",
    )

    case: Mapped[Optional["Case"]] = relationship(
        back_populates="notifications",
    )