from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Property(Base):
    """
    Represents a property listed by the estate agency.
    """

    __tablename__ = "properties"

    # =========================================================
    # IDENTITY
    # =========================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    listing_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    listing_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # =========================================================
    # BASIC LISTING INFORMATION
    # =========================================================

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    listing_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    status: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # =========================================================
    # PRICE
    # =========================================================

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="GBP",
        nullable=False,
    )

    price_period: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # =========================================================
    # PROPERTY INFORMATION
    # =========================================================

    property_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    bedrooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    bathrooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    reception_rooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    area_sqft: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    # =========================================================
    # LOCATION
    # =========================================================

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    locality: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    postcode: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # =========================================================
    # PROPERTY FEATURES
    # =========================================================

    parking: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    parking_spaces: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    garden: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    garage: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    balcony: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    terrace: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    furnished: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    pets_allowed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    # =========================================================
    # SALE INFORMATION
    # =========================================================

    tenure: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    epc_rating: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # =========================================================
    # FLEXIBLE PROPERTY DATA
    # =========================================================

    amenities: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    image_urls: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # =========================================================
    # ESTATE AGENT
    # =========================================================

    agent_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # RENTAL INFORMATION
    # =========================================================

    available_from: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # =========================================================
    # UI / INTERNAL
    # =========================================================

    # NOTE: is_featured was previously declared here but the column
    # doesn't actually exist in the DB, which broke every query that
    # selects a Property (UndefinedColumn). Removed until a migration
    # adds the column back. Re-add both this field and get_featured()
    # in db/crud/property.py together if/when that migration lands.

    # =========================================================
    # SCRAPING / TIMESTAMPS
    # =========================================================

    scraped_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    buyer_leads = relationship(
        "BuyerLead",
        back_populates="selected_property",
    )

    viewings = relationship(
        "Viewing",
        back_populates="property",
    )

    # =========================================================
    # REPRESENTATION
    # =========================================================

    def __repr__(self) -> str:

        return (
            f"<Property("
            f"title='{self.title}', "
            f"price={self.price}, "
            f"city='{self.city}')>"
        )