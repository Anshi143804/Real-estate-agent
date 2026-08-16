from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.crud.common import CRUDBase
from app.db.models.buyer import BuyerLead


class BuyerCRUD(CRUDBase[BuyerLead]):
    def __init__(self):
        super().__init__(BuyerLead)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create_buyer(
        self,
        db: Session,
        **kwargs,
    ) -> BuyerLead:
        return self.create(db, **kwargs)

    # ------------------------------------------------------------------
    # GETTERS
    # ------------------------------------------------------------------

    def get_buyer(
        self,
        db: Session,
        buyer_id: str,
    ) -> Optional[BuyerLead]:
        return self.get(db, buyer_id)

    def get_by_phone(
        self,
        db: Session,
        phone: str,
    ) -> Optional[BuyerLead]:

        stmt = (
            select(BuyerLead)
            .where(BuyerLead.phone == phone)
        )

        return db.scalar(stmt)

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> Optional[BuyerLead]:

        stmt = (
            select(BuyerLead)
            .where(BuyerLead.email.ilike(email))
        )

        return db.scalar(stmt)

    def get_active_buyers(
        self,
        db: Session,
    ) -> Sequence[BuyerLead]:

        stmt = (
            select(BuyerLead)
            .where(BuyerLead.is_active.is_(True))
            .order_by(BuyerLead.created_at.desc())
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def search(
        self,
        db: Session,
        *,
        city: Optional[str] = None,
        locality: Optional[str] = None,
        property_type: Optional[str] = None,
        listing_type: Optional[str] = None,
        min_budget: Optional[Decimal] = None,
        max_budget: Optional[Decimal] = None,
        bedrooms: Optional[int] = None,
    ) -> Sequence[BuyerLead]:

        filters = []

        if city:
            filters.append(BuyerLead.preferred_city.ilike(city))

        if locality:
            filters.append(BuyerLead.preferred_locality.ilike(locality))

        if property_type:
            filters.append(
                BuyerLead.preferred_property_type == property_type
            )

        if listing_type:
            filters.append(
                BuyerLead.preferred_listing_type == listing_type
            )

        if min_budget is not None:
            filters.append(BuyerLead.max_budget >= min_budget)

        if max_budget is not None:
            filters.append(BuyerLead.min_budget <= max_budget)

        if bedrooms is not None:
            filters.append(
                BuyerLead.minimum_bedrooms >= bedrooms
            )

        stmt = select(BuyerLead)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(BuyerLead.created_at.desc())

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update_buyer(
        self,
        db: Session,
        buyer: BuyerLead,
        **kwargs,
    ) -> BuyerLead:

        return self.update(
            db,
            buyer,
            **kwargs,
        )

    def update_budget(
        self,
        db: Session,
        buyer: BuyerLead,
        min_budget: Decimal,
        max_budget: Decimal,
    ) -> BuyerLead:

        buyer.min_budget = min_budget
        buyer.max_budget = max_budget

        db.commit()
        db.refresh(buyer)

        return buyer

    def update_preferences(
        self,
        db: Session,
        buyer: BuyerLead,
        **kwargs,
    ) -> BuyerLead:

        for key, value in kwargs.items():
            if hasattr(buyer, key):
                setattr(buyer, key, value)

        db.commit()
        db.refresh(buyer)

        return buyer

    def activate(
        self,
        db: Session,
        buyer: BuyerLead,
    ) -> BuyerLead:

        buyer.is_active = True

        db.commit()
        db.refresh(buyer)

        return buyer

    def deactivate(
        self,
        db: Session,
        buyer: BuyerLead,
    ) -> BuyerLead:

        buyer.is_active = False

        db.commit()
        db.refresh(buyer)

        return buyer

    # ------------------------------------------------------------------
    # MATCHING HELPERS
    # ------------------------------------------------------------------

    def get_matching_buyers(
        self,
        db: Session,
        *,
        city: str,
        property_type: str,
        listing_type: str,
        price: Decimal,
        bedrooms: int,
    ) -> Sequence[BuyerLead]:

        stmt = (
            select(BuyerLead)
            .where(
                BuyerLead.is_active.is_(True),
                BuyerLead.preferred_city.ilike(city),
                BuyerLead.preferred_property_type == property_type,
                BuyerLead.preferred_listing_type == listing_type,
                BuyerLead.min_budget <= price,
                BuyerLead.max_budget >= price,
                BuyerLead.minimum_bedrooms <= bedrooms,
            )
            .order_by(BuyerLead.created_at.desc())
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete_buyer(
        self,
        db: Session,
        buyer: BuyerLead,
    ) -> None:

        self.delete(
            db,
            buyer,
        )


buyer_repo = BuyerCRUD()