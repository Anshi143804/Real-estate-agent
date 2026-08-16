from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.crud.common import CRUDBase
from app.db.models.conversation import (
    ConversationSession,
    ConversationMessage,
)


class ConversationCRUD:
    """
    Repository for conversation sessions and messages.

    This repository is intentionally separate from CRUDBase because it
    manages two related models.
    """

    # ============================================================
    # SESSION OPERATIONS
    # ============================================================

    def create_session(
        self,
        db: Session,
        **kwargs,
    ) -> ConversationSession:

        session = ConversationSession(**kwargs)

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    def get_session(
        self,
        db: Session,
        session_id: str,
    ) -> Optional[ConversationSession]:

        return db.get(ConversationSession, session_id)

    def get_session_by_phone(
        self,
        db: Session,
        phone_number: str,
    ) -> Optional[ConversationSession]:

        stmt = (
            select(ConversationSession)
            .where(
                ConversationSession.phone_number == phone_number
            )
            .order_by(
                desc(ConversationSession.started_at)
            )
        )

        return db.scalar(stmt)

    def get_active_session(
        self,
        db: Session,
        phone_number: str,
    ) -> Optional[ConversationSession]:

        stmt = (
            select(ConversationSession)
            .where(
                ConversationSession.phone_number == phone_number,
                ConversationSession.status == "ACTIVE",
            )
            .order_by(
                desc(ConversationSession.started_at)
            )
        )

        return db.scalar(stmt)

    def end_session(
        self,
        db: Session,
        session: ConversationSession,
        summary: Optional[str] = None,
    ) -> ConversationSession:

        session.status = "COMPLETED"
        session.ended_at = datetime.utcnow()

        if summary:
            session.summary = summary

        db.commit()
        db.refresh(session)

        return session

    # ============================================================
    # MESSAGE OPERATIONS
    # ============================================================

    def save_message(
        self,
        db: Session,
        **kwargs,
    ) -> ConversationMessage:

        message = ConversationMessage(**kwargs)

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    def save_messages(
        self,
        db: Session,
        session_id: str,
        messages: Sequence[dict],
    ) -> int:
        """
        Bulk-insert an entire transcript in a single transaction.

        save_message() above does a commit + refresh per call (2 DB round
        trips per row - one to insert, one just to read the row back even
        though the caller doesn't use it). For a 40-50 message transcript
        that's 80-100 synchronous round trips during a live call. This
        does one INSERT batch + a single COMMIT for the whole transcript.

        Each dict in `messages` needs "speaker" and "message" keys.
        """

        objects = [
            ConversationMessage(
                session_id=session_id,
                speaker=m["speaker"],
                message=m["message"],
            )
            for m in messages
        ]

        if not objects:
            return 0

        db.add_all(objects)
        db.commit()

        return len(objects)

    def get_messages(
        self,
        db: Session,
        session_id: str,
    ) -> Sequence[ConversationMessage]:

        stmt = (
            select(ConversationMessage)
            .where(
                ConversationMessage.session_id == session_id
            )
            .order_by(
                ConversationMessage.created_at
            )
        )

        return db.scalars(stmt).all()

    def get_recent_messages(
        self,
        db: Session,
        session_id: str,
        limit: int = 20,
    ) -> Sequence[ConversationMessage]:

        stmt = (
            select(ConversationMessage)
            .where(
                ConversationMessage.session_id == session_id
            )
            .order_by(
                desc(ConversationMessage.created_at)
            )
            .limit(limit)
        )

        messages = db.scalars(stmt).all()

        return list(reversed(messages))

    # ============================================================
    # SEARCH
    # ============================================================

    def get_sessions_by_property(
        self,
        db: Session,
        property_id: str,
    ) -> Sequence[ConversationSession]:

        stmt = (
            select(ConversationSession)
            .where(
                ConversationSession.property_id == property_id
            )
            .order_by(
                desc(ConversationSession.started_at)
            )
        )

        return db.scalars(stmt).all()

    def get_sessions_by_buyer(
        self,
        db: Session,
        buyer_id: str,
    ) -> Sequence[ConversationSession]:

        stmt = (
            select(ConversationSession)
            .where(
                ConversationSession.buyer_id == buyer_id
            )
            .order_by(
                desc(ConversationSession.started_at)
            )
        )

        return db.scalars(stmt).all()

    def get_sessions_by_seller(
        self,
        db: Session,
        seller_id: str,
    ) -> Sequence[ConversationSession]:

        stmt = (
            select(ConversationSession)
            .where(
                ConversationSession.seller_id == seller_id
            )
            .order_by(
                desc(ConversationSession.started_at)
            )
        )

        return db.scalars(stmt).all()

    # ============================================================
    # AI HELPERS
    # ============================================================

    def update_summary(
        self,
        db: Session,
        session: ConversationSession,
        summary: str,
    ) -> ConversationSession:

        session.summary = summary

        db.commit()
        db.refresh(session)

        return session

    def update_sentiment(
        self,
        db: Session,
        session: ConversationSession,
        sentiment: str,
    ) -> ConversationSession:

        session.sentiment = sentiment

        db.commit()
        db.refresh(session)

        return session

    def increment_token_usage(
        self,
        db: Session,
        session: ConversationSession,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> ConversationSession:

        session.prompt_tokens += prompt_tokens
        session.completion_tokens += completion_tokens
        session.total_tokens += (
            prompt_tokens + completion_tokens
        )

        db.commit()
        db.refresh(session)

        return session

    # ============================================================
    # DELETE
    # ============================================================

    def delete_session(
        self,
        db: Session,
        session: ConversationSession,
    ) -> None:

        db.delete(session)
        db.commit()


conversation_repo = ConversationCRUD()