"""
app/db/models/evaluation.py

Evaluation model for assessing conversation quality and recommendation accuracy.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ConversationEvaluation(Base):
    """
    Stores evaluation scores and feedback for a completed conversation.
    Evaluation happens asynchronously after the call ends, analyzing:
    - Requirement understanding
    - Property relevance
    - Conversation quality
    - Tool/search usage
    - Recommendation quality
    - Call completion
    """

    __tablename__ = "conversation_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Overall score (0-100)
    overall_score: Mapped[int | None] = mapped_column(
        Integer,
    )

    # Category scores (0-100 each)
    requirement_understanding: Mapped[int | None] = mapped_column(Integer)
    property_relevance: Mapped[int | None] = mapped_column(Integer)
    conversation_quality: Mapped[int | None] = mapped_column(Integer)
    search_tool_usage: Mapped[int | None] = mapped_column(Integer)
    recommendation_quality: Mapped[int | None] = mapped_column(Integer)
    transcript_quality: Mapped[int | None] = mapped_column(Integer)
    call_completion: Mapped[int | None] = mapped_column(Integer)

    # Structured feedback
    strengths: Mapped[list | None] = mapped_column(
        JSONB,
    )

    issues: Mapped[list | None] = mapped_column(
        JSONB,
    )

    # Raw evaluation data (for debugging/transparency)
    evaluation_details: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    # Timestamp
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # Relationship
    session = relationship(
        "ConversationSession",
        backref="evaluation",
    )

    def __repr__(self):
        return (
            f"<ConversationEvaluation("
            f"id={self.id}, "
            f"session_id={self.session_id}, "
            f"overall_score={self.overall_score})>"
        )
