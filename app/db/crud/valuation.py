from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.crud.common import CRUDBase
from app.db.models.valuation import Valuation


class ValuationCRUD(CRUDBase[Valuation]):
    def __init__(self):
        super().__init__(Valuation)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create_valuation(
        self,
        db: Session,
        **kwargs,
    ) -> Valuation:
        return self.create(db, **kwargs)

    # ------------------------------------------------------------------
    # GETTERS
    # ------------------------------------------------------------------

    def get_valuation(
        self,
        db: Session,
        valuation_id: str,
    ) -> Optional[Valuation]:
        return self.get(db, valuation_id)

    def get_by_property(
        self,
        db: Session,
        property_id: str,
    ) -> Sequence[Valuation]:

        stmt = (
            select(Valuation)
            .where(Valuation.property_id == property_id)
            .order_by(Valuation.created_at.desc())
        )

        return db.scalars(stmt).all()

    def get_by_seller(
        self,
        db: Session,
        seller_id: str,
    ) -> Sequence[Valuation]:

        stmt = (
            select(Valuation)
            .where(Valuation.seller_id == seller_id)
            .order_by(Valuation.created_at.desc())
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    def get_pending(
        self,
        db: Session,
    ) -> Sequence[Valuation]:

        stmt = (
            select(Valuation)
            .where(Valuation.status == "PENDING")
            .order_by(Valuation.scheduled_at)
        )

        return db.scalars(stmt).all()

    def get_scheduled(
        self,
        db: Session,
    ) -> Sequence[Valuation]:

        stmt = (
            select(Valuation)
            .where(Valuation.status == "SCHEDULED")
            .order_by(Valuation.scheduled_at)
        )

        return db.scalars(stmt).all()

    def get_completed(
        self,
        db: Session,
    ) -> Sequence[Valuation]:

        stmt = (
            select(Valuation)
            .where(Valuation.status == "COMPLETED")
            .order_by(Valuation.completed_at.desc())
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # SCHEDULING
    # ------------------------------------------------------------------

    def schedule(
        self,
        db: Session,
        valuation: Valuation,
        scheduled_at: datetime,
    ) -> Valuation:

        valuation.scheduled_at = scheduled_at
        valuation.status = "SCHEDULED"

        db.commit()
        db.refresh(valuation)

        return valuation

    def reschedule(
        self,
        db: Session,
        valuation: Valuation,
        scheduled_at: datetime,
    ) -> Valuation:

        valuation.scheduled_at = scheduled_at

        db.commit()
        db.refresh(valuation)

        return valuation

    # ------------------------------------------------------------------
    # COMPLETION
    # ------------------------------------------------------------------

    def complete(
        self,
        db: Session,
        valuation: Valuation,
        estimated_price: Decimal,
        notes: Optional[str] = None,
    ) -> Valuation:

        valuation.status = "COMPLETED"
        valuation.estimated_price = estimated_price
        valuation.completed_at = datetime.utcnow()

        if notes and hasattr(valuation, "valuation_notes"):
            valuation.valuation_notes = notes

        db.commit()
        db.refresh(valuation)

        return valuation

    def cancel(
        self,
        db: Session,
        valuation: Valuation,
        reason: Optional[str] = None,
    ) -> Valuation:

        valuation.status = "CANCELLED"

        if reason and hasattr(valuation, "cancellation_reason"):
            valuation.cancellation_reason = reason

        db.commit()
        db.refresh(valuation)

        return valuation

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def get_between(
        self,
        db: Session,
        start: datetime,
        end: datetime,
    ) -> Sequence[Valuation]:

        stmt = (
            select(Valuation)
            .where(
                and_(
                    Valuation.scheduled_at >= start,
                    Valuation.scheduled_at <= end,
                )
            )
            .order_by(Valuation.scheduled_at)
        )

        return db.scalars(stmt).all()

    def get_due_today(
        self,
        db: Session,
        start: datetime,
        end: datetime,
    ) -> Sequence[Valuation]:

        stmt = (
            select(Valuation)
            .where(
                Valuation.status == "SCHEDULED",
                Valuation.scheduled_at >= start,
                Valuation.scheduled_at <= end,
            )
            .order_by(Valuation.scheduled_at)
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # ANALYTICS
    # ------------------------------------------------------------------

    def average_estimated_price(
        self,
        db: Session,
    ) -> Optional[Decimal]:

        valuations = self.get_completed(db)

        if not valuations:
            return None

        total = sum(v.estimated_price for v in valuations)

        return total / len(valuations)

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete_valuation(
        self,
        db: Session,
        valuation: Valuation,
    ) -> None:

        self.delete(
            db,
            valuation,
        )


valuation_repo = ValuationCRUD()