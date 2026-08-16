from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.crud.common import CRUDBase
from app.db.models.property import Property


class PropertyCRUD(CRUDBase[Property]):
    def __init__(self):
        super().__init__(Property)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create_property(self, db: Session, **kwargs) -> Property:
        return self.create(db, **kwargs)

    # ------------------------------------------------------------------
    # GETTERS
    # ------------------------------------------------------------------

    def get_property(
        self,
        db: Session,
        property_id: str,
    ) -> Optional[Property]:
        return self.get(db, property_id)

    def get_by_reference(
        self,
        db: Session,
        reference_number: str,
    ) -> Optional[Property]:

        stmt = (
            select(Property)
            .where(Property.reference_number == reference_number)
        )

        return db.scalar(stmt)

    def get_available(
        self,
        db: Session,
    ) -> Sequence[Property]:

        stmt = (
            select(Property)
            .where(Property.status == "AVAILABLE")
        )

        return db.scalars(stmt).all()

    def get_by_city(
        self,
        db: Session,
        city: str,
    ) -> Sequence[Property]:

        stmt = (
            select(Property)
            .where(Property.city.ilike(city))
        )

        return db.scalars(stmt).all()

    def get_by_locality(
        self,
        db: Session,
        locality: str,
    ) -> Sequence[Property]:

        stmt = (
            select(Property)
            .where(Property.locality.ilike(locality))
        )

        return db.scalars(stmt).all()

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def search(
    self,
    db: Session,
    city: str = None,
    locality: str = None,
    property_type: str = None,
    listing_type: str = None,
    min_price: float = None,
    max_price: float = None,
    bedrooms: int = None,
    bathrooms: int = None,
    reception_rooms: int = None,
    min_area_sqft: float = None,
    max_area_sqft: float = None,
    furnished: str = None,
    parking: bool = None,
    garden: bool = None,
    garage: bool = None,
    balcony: bool = None,
    terrace: bool = None,
    pets_allowed: bool = None,
    tenure: str = None,
    status: str = "available",
):
        query = db.query(Property)

        # 1. Case-insensitive status match (matches 'available', 'AVAILABLE', 'Available')
        if status:
            query = query.filter(Property.status.ilike(f"%{status}%"))

        # 2. Case-insensitive city match
        if city:
            query = query.filter(Property.city.ilike(f"%{city}%"))

        # 3. Case-insensitive locality match
        if locality:
            query = query.filter(Property.locality.ilike(f"%{locality}%"))

        # 4. Case-insensitive property_type match
        if property_type:
            query = query.filter(Property.property_type.ilike(f"%{property_type}%"))

        # 5. Case-insensitive listing_type match
        if listing_type:
            query = query.filter(Property.listing_type.ilike(f"%{listing_type}%"))

        # 6. Bedrooms / bathrooms / reception rooms - "at least N"
        if bedrooms is not None:
            query = query.filter(Property.bedrooms >= bedrooms)

        if bathrooms is not None:
            query = query.filter(Property.bathrooms >= bathrooms)

        if reception_rooms is not None:
            query = query.filter(Property.reception_rooms >= reception_rooms)

        # 7. Price range
        if min_price is not None:
            query = query.filter(Property.price >= min_price)

        if max_price is not None:
            query = query.filter(Property.price <= max_price)

        # 8. Property size range
        if min_area_sqft is not None:
            query = query.filter(Property.area_sqft >= min_area_sqft)

        if max_area_sqft is not None:
            query = query.filter(Property.area_sqft <= max_area_sqft)

        # 9. Rental attributes
        if furnished:
            query = query.filter(Property.furnished.ilike(f"%{furnished}%"))

        if pets_allowed is not None:
            query = query.filter(Property.pets_allowed == pets_allowed)

        # 10. Boolean features - only filter when the buyer actually
        # requires them (True). A False/None value means "no preference",
        # not "must not have it".
        if parking:
            query = query.filter(Property.parking.is_(True))

        if garden:
            query = query.filter(Property.garden.is_(True))

        if garage:
            query = query.filter(Property.garage.is_(True))

        if balcony:
            query = query.filter(Property.balcony.is_(True))

        if terrace:
            query = query.filter(Property.terrace.is_(True))

        # 11. Tenure
        if tenure:
            query = query.filter(Property.tenure.ilike(f"%{tenure}%"))

        return query.order_by(Property.created_at.desc()).all()

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update_property(
        self,
        db: Session,
        property_obj: Property,
        **kwargs,
    ) -> Property:

        return self.update(
            db,
            property_obj,
            **kwargs,
        )

    def update_price(
        self,
        db: Session,
        property_obj: Property,
        new_price: Decimal,
    ) -> Property:

        property_obj.price = new_price

        db.commit()
        db.refresh(property_obj)

        return property_obj

    def update_status(
        self,
        db: Session,
        property_obj: Property,
        status: str,
    ) -> Property:

        property_obj.status = status

        db.commit()
        db.refresh(property_obj)

        return property_obj

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete_property(
        self,
        db: Session,
        property_obj: Property,
    ) -> None:

        self.delete(
            db,
            property_obj,
        )


property_repo = PropertyCRUD()