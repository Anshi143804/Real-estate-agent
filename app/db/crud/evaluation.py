"""
app/db/crud/evaluation.py

CRUD operations for conversation evaluations.
"""

from __future__ import annotations

from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.evaluation import ConversationEvaluation


class EvaluationCRUD:
    """Repository for conversation evaluations."""

    def create_evaluation(
        self,
        db: Session,
        session_id: uuid.UUID,
        overall_score: Optional[int] = None,
        requirement_understanding: Optional[int] = None,
        property_relevance: Optional[int] = None,
        conversation_quality: Optional[int] = None,
        search_tool_usage: Optional[int] = None,
        recommendation_quality: Optional[int] = None,
        transcript_quality: Optional[int] = None,
        call_completion: Optional[int] = None,
        strengths: Optional[list] = None,
        issues: Optional[list] = None,
        evaluation_details: Optional[dict] = None,
    ) -> ConversationEvaluation:
        """Create a new conversation evaluation record."""

        evaluation = ConversationEvaluation(
            session_id=session_id,
            overall_score=overall_score,
            requirement_understanding=requirement_understanding,
            property_relevance=property_relevance,
            conversation_quality=conversation_quality,
            search_tool_usage=search_tool_usage,
            recommendation_quality=recommendation_quality,
            transcript_quality=transcript_quality,
            call_completion=call_completion,
            strengths=strengths or [],
            issues=issues or [],
            evaluation_details=evaluation_details or {},
        )

        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        return evaluation

    def get_evaluation(
        self,
        db: Session,
        session_id: uuid.UUID,
    ) -> Optional[ConversationEvaluation]:
        """Retrieve evaluation for a conversation session."""

        stmt = select(ConversationEvaluation).where(
            ConversationEvaluation.session_id == session_id
        )
        return db.scalar(stmt)

    def update_evaluation(
        self,
        db: Session,
        session_id: uuid.UUID,
        **kwargs,
    ) -> Optional[ConversationEvaluation]:
        """Update an existing evaluation."""

        evaluation = self.get_evaluation(db, session_id)
        if evaluation:
            for key, value in kwargs.items():
                if hasattr(evaluation, key):
                    setattr(evaluation, key, value)
            db.commit()
            db.refresh(evaluation)
        return evaluation


# Create singleton instance
evaluation_repo = EvaluationCRUD()
