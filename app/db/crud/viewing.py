from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.db.crud.common import CRUDBase
from app.db.models.viewing import Viewing


class ViewingCRUD(CRUDBase[Viewing]):
    def __init__(self):
        super().__init__(Viewing)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def schedule_viewing(
        self,
        db: Session,
        **kwargs,
    ) -> Viewing:
        return self.create(db, **kwargs)

    # ------------------------------------------------------------------
    # GETTERS
    # ------------------------------------------------------------------

    def get_viewing(
        self,
        db: Session,
        viewing_id: str,
    ) -> Optional[Viewing]:
        return self.get(db, viewing_id)

    def get_by_property(
        self,
        db: Session,
        property_id: str,
    ) -> Sequence[Viewing]:

        stmt = (
            select(Viewing)
            .where(Viewing.property_id == property_id)
            .order_by(Viewing.scheduled_at.desc())
        )

        return db.scalars(stmt).all()

    def get_by_buyer(
        self,
        db: Session,
        buyer_id: str,
    ) -> Sequence[Viewing]:

        stmt = (
            select(Viewing)
            .where(Viewing.buyer_id == buyer_id)
            .order_by(Viewing.scheduled_at.desc())
        )

        return db.scalars(stmt).all()

    def get_by_agent(
        self,
        db: Session,
        agent_id: str,
    ) -> Sequence[Viewing]:

        stmt = (
            select(Viewing)
            .where(Viewing.agent_id == agent_id)
            .order_by(Viewing.scheduled_at.desc())
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # UPCOMING
    # ------------------------------------------------------------------

    def get_upcoming(
        self,
        db: Session,
    ) -> Sequence[Viewing]:

        stmt = (
            select(Viewing)
            .where(
                Viewing.scheduled_at >= datetime.utcnow(),
                Viewing.status == "SCHEDULED",
            )
            .order_by(Viewing.scheduled_at)
        )

        return db.scalars(stmt).all()

    def get_today(
        self,
        db: Session,
        start: datetime,
        end: datetime,
    ) -> Sequence[Viewing]:

        stmt = (
            select(Viewing)
            .where(
                Viewing.scheduled_at >= start,
                Viewing.scheduled_at <= end,
            )
            .order_by(Viewing.scheduled_at)
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # CONFLICT CHECKING
    # ------------------------------------------------------------------

    def has_property_conflict(
        self,
        db: Session,
        property_id: str,
        scheduled_at: datetime,
    ) -> bool:

        stmt = (
            select(Viewing)
            .where(
                Viewing.property_id == property_id,
                Viewing.scheduled_at == scheduled_at,
                Viewing.status == "SCHEDULED",
            )
        )

        return db.scalar(stmt) is not None

    def has_buyer_conflict(
        self,
        db: Session,
        buyer_id: str,
        scheduled_at: datetime,
    ) -> bool:

        stmt = (
            select(Viewing)
            .where(
                Viewing.buyer_id == buyer_id,
                Viewing.scheduled_at == scheduled_at,
                Viewing.status == "SCHEDULED",
            )
        )

        return db.scalar(stmt) is not None

    def has_agent_conflict(
        self,
        db: Session,
        agent_id: str,
        scheduled_at: datetime,
    ) -> bool:

        stmt = (
            select(Viewing)
            .where(
                Viewing.agent_id == agent_id,
                Viewing.scheduled_at == scheduled_at,
                Viewing.status == "SCHEDULED",
            )
        )

        return db.scalar(stmt) is not None

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    def reschedule(
        self,
        db: Session,
        viewing: Viewing,
        scheduled_at: datetime,
    ) -> Viewing:

        viewing.scheduled_at = scheduled_at

        db.commit()
        db.refresh(viewing)

        return viewing

    def complete(
        self,
        db: Session,
        viewing: Viewing,
    ) -> Viewing:

        viewing.status = "COMPLETED"

        db.commit()
        db.refresh(viewing)

        return viewing

    def cancel(
        self,
        db: Session,
        viewing: Viewing,
        reason: Optional[str] = None,
    ) -> Viewing:

        viewing.status = "CANCELLED"

        if reason and hasattr(viewing, "cancellation_reason"):
            viewing.cancellation_reason = reason

        db.commit()
        db.refresh(viewing)

        return viewing

    def mark_no_show(
        self,
        db: Session,
        viewing: Viewing,
    ) -> Viewing:

        viewing.status = "NO_SHOW"

        db.commit()
        db.refresh(viewing)

        return viewing

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def get_by_status(
        self,
        db: Session,
        status: str,
    ) -> Sequence[Viewing]:

        stmt = (
            select(Viewing)
            .where(Viewing.status == status)
            .order_by(Viewing.scheduled_at.desc())
        )

        return db.scalars(stmt).all()

    def get_between(
        self,
        db: Session,
        start: datetime,
        end: datetime,
    ) -> Sequence[Viewing]:

        stmt = (
            select(Viewing)
            .where(
                and_(
                    Viewing.scheduled_at >= start,
                    Viewing.scheduled_at <= end,
                )
            )
            .order_by(Viewing.scheduled_at)
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete_viewing(
        self,
        db: Session,
        viewing: Viewing,
    ) -> None:

        self.delete(
            db,
            viewing,
        )


viewing_repo = ViewingCRUD()