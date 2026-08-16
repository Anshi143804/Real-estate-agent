from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SellerLead(Base):
    """
    Represents a seller lead.
    """

    __tablename__ = "seller_leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # -------------------------
    # Contact Information
    # -------------------------

    name: Mapped[str | None] = mapped_column(String)

    email: Mapped[str | None] = mapped_column(String)

    phone: Mapped[str | None] = mapped_column(String)

    # -------------------------
    # Property Information
    # -------------------------

    property_address: Mapped[str | None] = mapped_column(Text)

    property_type: Mapped[str | None] = mapped_column(String)

    bedrooms: Mapped[int | None] = mapped_column(Integer)

    bathrooms: Mapped[int | None] = mapped_column(Integer)

    estimated_value: Mapped[float | None] = mapped_column(
        Numeric(12, 2)
    )

    occupied: Mapped[bool | None] = mapped_column(Boolean)

    # -------------------------
    # Seller Information
    # -------------------------

    reason_for_selling: Mapped[str | None] = mapped_column(Text)

    selling_timeline: Mapped[str | None] = mapped_column(String)

    preferred_contact_time: Mapped[str | None] = mapped_column(String)

    valuation_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    # -------------------------
    # Lead Information
    # -------------------------

    status: Mapped[str] = mapped_column(
        String,
        default="New",
    )

    lead_score: Mapped[int | None] = mapped_column(Integer)

    # -------------------------
    # AI Summary
    # -------------------------

    summary_text: Mapped[str | None] = mapped_column(Text)

    summary_json: Mapped[dict | None] = mapped_column(JSONB)

    # -------------------------
    # Timestamps
    # -------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # -------------------------
    # Relationships
    # -------------------------

    valuations = relationship(
        "Valuation",
        back_populates="seller_lead",
        cascade="all, delete-orphan",
    )
    
    conversation_sessions = relationship(
        "ConversationSession",
        back_populates="seller_lead",
        cascade="all, delete-orphan",
    )
    def __repr__(self):

        return (
            f"<SellerLead("
            f"name='{self.name}', "
            f"address='{self.property_address}', "
            f"status='{self.status}')>"
        )