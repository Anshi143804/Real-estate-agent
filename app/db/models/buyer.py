from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class BuyerLead(Base):
    """
    Represents a qualified buyer lead.
    """

    __tablename__ = "buyer_leads"

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
    # Lead Status
    # -------------------------

    status: Mapped[str] = mapped_column(
        String,
        default="New",
    )

    # -------------------------
    # Buyer Requirements
    # -------------------------

    budget_min: Mapped[float | None] = mapped_column(
        Numeric(12, 2)
    )

    budget_max: Mapped[float | None] = mapped_column(
        Numeric(12, 2)
    )

    preferred_locations: Mapped[dict | list | None] = mapped_column(
        JSONB
    )

    property_type: Mapped[str | None] = mapped_column(
        String
    )

    bedrooms: Mapped[int | None] = mapped_column(
        Integer
    )

    bathrooms: Mapped[int | None] = mapped_column(
        Integer
    )

    parking_required: Mapped[bool | None] = mapped_column(
        Boolean
    )

    garden_required: Mapped[bool | None] = mapped_column(
        Boolean
    )

    # -------------------------
    # Financial Qualification
    # -------------------------

    mortgage_status: Mapped[str | None] = mapped_column(
        String
    )

    deposit_percentage: Mapped[int | None] = mapped_column(
        Integer
    )

    first_time_buyer: Mapped[bool | None] = mapped_column(
        Boolean
    )

    chain_status: Mapped[str | None] = mapped_column(
        String
    )

    moving_timeline: Mapped[str | None] = mapped_column(
        String
    )

    # -------------------------
    # Property Selected
    # -------------------------

    selected_property_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id"),
    )

    selected_property_url: Mapped[str | None] = mapped_column(
        Text
    )

    # -------------------------
    # AI Summary
    # -------------------------

    summary_text: Mapped[str | None] = mapped_column(
        Text
    )

    summary_json: Mapped[dict | None] = mapped_column(
        JSONB
    )

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

    selected_property = relationship(
        "Property",
        back_populates="buyer_leads",
    )

    viewings = relationship(
        "Viewing",
        back_populates="buyer_lead",
        cascade="all, delete-orphan",
    )
    conversation_sessions = relationship(
        "ConversationSession",
        back_populates="buyer_lead",
        cascade="all, delete-orphan",
    )

    def __repr__(self):

        return (
            f"<BuyerLead("
            f"name='{self.name}', "
            f"budget={self.budget_max}, "
            f"status='{self.status}')>"
        )