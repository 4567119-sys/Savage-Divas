
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    preferred_language: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    accessibility_mode: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    total_net_worth: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    monthly_income: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    goals: Mapped[List["FinancialGoal"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )

    life_events: Mapped[List["LifeEvent"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )

    cases: Mapped[List["Case"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )

    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )


class FinancialGoal(Base):
    __tablename__ = "financial_goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_amount: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    current_amount: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    target_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="IN_PROGRESS",
        nullable=False,
    )

    client: Mapped["Client"] = relationship(back_populates="goals")


class LifeEvent(Base):
    __tablename__ = "life_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    event_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True
    )
    financial_impact: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    client: Mapped["Client"] = relationship(back_populates="life_events")

