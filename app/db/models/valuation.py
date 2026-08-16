from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Valuation(Base):
    """
    Represents a property valuation appointment.
    """

    __tablename__ = "valuations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # -------------------------
    # Relationships
    # -------------------------

    seller_lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("seller_leads.id", ondelete="CASCADE"),
        nullable=False,
    )

    # -------------------------
    # Appointment
    # -------------------------

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime,
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
    # Audit
    # -------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # -------------------------
    # ORM Relationships
    # -------------------------

    seller_lead = relationship(
        "SellerLead",
        back_populates="valuations",
    )

    def __repr__(self):
        return (
            f"<Valuation("
            f"seller={self.seller_lead_id}, "
            f"scheduled_at={self.scheduled_at})>"
        )