from __future__ import annotations

import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Viewing(Base):
    """
    Represents a booked property viewing.
    """

    __tablename__ = "viewings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # -------------------------
    # Relationships
    # -------------------------

    buyer_lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buyer_leads.id", ondelete="CASCADE"),
        nullable=False,
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
    )

    # -------------------------
    # Viewing Details
    # -------------------------

    viewing_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    viewing_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        default="Booked",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
    )

    # -------------------------
    # Timestamp
    # -------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # -------------------------
    # ORM Relationships
    # -------------------------

    buyer_lead = relationship(
        "BuyerLead",
        back_populates="viewings",
    )

    property = relationship(
        "Property",
        back_populates="viewings",
    )

    def __repr__(self):
        return (
            f"<Viewing("
            f"buyer={self.buyer_lead_id}, "
            f"property={self.property_id}, "
            f"date={self.viewing_date}, "
            f"time={self.viewing_time})>"
        )