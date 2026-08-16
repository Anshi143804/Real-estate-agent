from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ==========================================================
# Conversation Session
# ==========================================================

class ConversationSession(Base):
    """
    Represents one complete AI conversation.
    """

    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Nullable because a session is either Buyer OR Seller
    buyer_lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buyer_leads.id", ondelete="CASCADE"),
    )

    seller_lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("seller_leads.id", ondelete="CASCADE"),
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # Populated by conversation_analysis_handler / finalize_conversation_handler
    # once the call ends (see app/tools/buyer/finalise_conversation.py).
    status: Mapped[str | None] = mapped_column(
        String,
        default="ACTIVE",
    )

    phone_number: Mapped[str | None] = mapped_column(
        String,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
    )

    analysis: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # Relationships

    buyer_lead = relationship(
        "BuyerLead",
        back_populates="conversation_sessions",
    )

    seller_lead = relationship(
        "SellerLead",
        back_populates="conversation_sessions",
    )

    messages = relationship(
        "ConversationMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<ConversationSession("
            f"id={self.id}, "
            f"completed={self.completed})>"
        )


# ==========================================================
# Conversation Message
# ==========================================================

class ConversationMessage(Base):
    """
    One message exchanged during a conversation.
    """

    __tablename__ = "conversation_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "conversation_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    speaker: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    session = relationship(
        "ConversationSession",
        back_populates="messages",
    )

    def __repr__(self):
        return (
            f"<ConversationMessage("
            f"speaker='{self.speaker}')>"
        )