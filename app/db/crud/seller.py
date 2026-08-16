from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.crud.common import CRUDBase
from app.db.models.seller import SellerLead


class SellerCRUD(CRUDBase[SellerLead]):
    def __init__(self):
        super().__init__(SellerLead)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create_seller(
        self,
        db: Session,
        **kwargs,
    ) -> SellerLead:
        return self.create(db, **kwargs)

    # ------------------------------------------------------------------
    # GETTERS
    # ------------------------------------------------------------------

    def get_seller(
        self,
        db: Session,
        seller_id: str,
    ) -> Optional[SellerLead]:
        return self.get(db, seller_id)

    def get_by_phone(
        self,
        db: Session,
        phone: str,
    ) -> Optional[SellerLead]:

        stmt = (
            select(SellerLead)
            .where(SellerLead.phone_number == phone)
        )

        return db.scalar(stmt)

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> Optional[SellerLead]:

        stmt = (
            select(SellerLead)
            .where(SellerLead.email.ilike(email))
        )

        return db.scalar(stmt)

    def get_active_sellers(
        self,
        db: Session,
    ) -> Sequence[SellerLead]:

        stmt = (
            select(SellerLead)
            .where(SellerLead.is_active.is_(True))
            .order_by(SellerLead.created_at.desc())
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
        min_expected_price: Optional[Decimal] = None,
        max_expected_price: Optional[Decimal] = None,
    ) -> Sequence[SellerLead]:

        filters = []

        if city:
            filters.append(
                SellerLead.property_city.ilike(city)
            )

        if locality:
            filters.append(
                SellerLead.property_locality.ilike(locality)
            )

        if property_type:
            filters.append(
                SellerLead.property_type == property_type
            )

        if listing_type:
            filters.append(
                SellerLead.listing_type == listing_type
            )

        if min_expected_price is not None:
            filters.append(
                SellerLead.expected_price >= min_expected_price
            )

        if max_expected_price is not None:
            filters.append(
                SellerLead.expected_price <= max_expected_price
            )

        stmt = select(SellerLead)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(SellerLead.created_at.desc())

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update_seller(
        self,
        db: Session,
        seller: SellerLead,
        **kwargs,
    ) -> SellerLead:

        return self.update(
            db,
            seller,
            **kwargs,
        )

    def update_expected_price(
        self,
        db: Session,
        seller: SellerLead,
        expected_price: Decimal,
    ) -> SellerLead:

        seller.expected_price = expected_price

        db.commit()
        db.refresh(seller)

        return seller

    def update_listing_status(
        self,
        db: Session,
        seller: SellerLead,
        status: str,
    ) -> SellerLead:

        seller.listing_status = status

        db.commit()
        db.refresh(seller)

        return seller

    def activate(
        self,
        db: Session,
        seller: SellerLead,
    ) -> SellerLead:

        seller.is_active = True

        db.commit()
        db.refresh(seller)

        return seller

    def deactivate(
        self,
        db: Session,
        seller: SellerLead,
    ) -> SellerLead:

        seller.is_active = False

        db.commit()
        db.refresh(seller)

        return seller

    # ------------------------------------------------------------------
    # LEAD HELPERS
    # ------------------------------------------------------------------

    def get_pending_listings(
        self,
        db: Session,
    ) -> Sequence[SellerLead]:

        stmt = (
            select(SellerLead)
            .where(
                SellerLead.listing_status == "PENDING"
            )
            .order_by(SellerLead.created_at.desc())
        )

        return db.scalars(stmt).all()

    def get_ready_for_listing(
        self,
        db: Session,
    ) -> Sequence[SellerLead]:

        stmt = (
            select(SellerLead)
            .where(
                SellerLead.listing_status == "APPROVED"
            )
            .order_by(SellerLead.created_at.desc())
        )

        return db.scalars(stmt).all()

    def get_needing_valuation(
        self,
        db: Session,
    ) -> Sequence[SellerLead]:

        stmt = (
            select(SellerLead)
            .where(
                SellerLead.valuation_completed.is_(False)
            )
            .order_by(SellerLead.created_at.asc())
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete_seller(
        self,
        db: Session,
        seller: SellerLead,
    ) -> None:

        self.delete(
            db,
            seller,
        )


seller_repo = SellerCRUD()