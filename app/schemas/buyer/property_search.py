"""
Schemas for the find_matching_properties tool.
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class PropertySearchRequest(BaseModel):
    """Requirements collected from the buyer/renter conversation."""

    # =========================================================
    # LOCATION
    # =========================================================

    city: str = Field(
        ...,
        description="Preferred city",
    )

    locality: Optional[str] = Field(
        default=None,
        description="Preferred locality, neighborhood, or area",
    )

    # =========================================================
    # PROPERTY
    # =========================================================

    property_type: Optional[str] = Field(
        default=None,
        description=(
            "Apartment, Flat, House, Villa, Detached house, "
            "Terraced house, Semi-detached house, Bungalow, etc."
        ),
    )

    listing_type: str = Field(
        default="sale",
        description="Whether the user wants to buy or rent: sale or rent",
    )

    # =========================================================
    # BUDGET
    # =========================================================

    min_budget: Optional[Decimal] = Field(
        default=None,
        description="Minimum purchase price or monthly rent",
    )

    max_budget: Optional[Decimal] = Field(
        default=None,
        description="Maximum purchase price or monthly rent",
    )

    # =========================================================
    # ROOMS
    # =========================================================

    min_bedrooms: Optional[int] = Field(
        default=None,
        description="Minimum number of bedrooms",
    )

    min_bathrooms: Optional[int] = Field(
        default=None,
        description="Minimum number of bathrooms",
    )

    min_reception_rooms: Optional[int] = Field(
        default=None,
        description="Minimum number of reception rooms",
    )

    # =========================================================
    # PROPERTY SIZE
    # =========================================================

    min_area_sqft: Optional[float] = Field(
        default=None,
        description="Minimum property size in square feet",
    )

    max_area_sqft: Optional[float] = Field(
        default=None,
        description="Maximum property size in square feet",
    )

    # =========================================================
    # RENTAL
    # =========================================================

    furnished: Optional[str] = Field(
        default=None,
        description=(
            "Furnished, unfurnished, or part-furnished"
        ),
    )

    pets_allowed: Optional[bool] = Field(
        default=None,
        description="Whether pets must be allowed",
    )

    # =========================================================
    # FEATURES
    # =========================================================

    parking: Optional[bool] = Field(
        default=None,
        description="Whether parking is required",
    )

    garden: Optional[bool] = Field(
        default=None,
        description="Whether a garden is required",
    )

    garage: Optional[bool] = Field(
        default=None,
        description="Whether a garage is required",
    )

    balcony: Optional[bool] = Field(
        default=None,
        description="Whether a balcony is required",
    )

    terrace: Optional[bool] = Field(
        default=None,
        description="Whether a terrace is required",
    )

    # =========================================================
    # SALE
    # =========================================================

    tenure: Optional[str] = Field(
        default=None,
        description="Freehold or leasehold",
    )

    # =========================================================
    # OTHER FEATURES
    # =========================================================

    features: List[str] = Field(
        default_factory=list,
        description=(
            "Additional requirements such as fireplace, "
            "utility room, period features, double glazing, "
            "south-facing garden, etc."
        ),
    )


class MatchedProperty(BaseModel):
    """
    Property summary shown to the buyer or renter.

    property_id and property_url are kept in the structured
    response for the application/UI. They should not be spoken
    aloud by the voice agent.
    """

    # =========================================================
    # IDENTITY
    # =========================================================

    property_id: str

    title: str

    # =========================================================
    # PRICE
    # =========================================================

    price: Decimal

    currency: str = "GBP"

    price_period: Optional[str] = None

    # =========================================================
    # LOCATION
    # =========================================================

    location: str

    postcode: Optional[str] = None

    # =========================================================
    # PROPERTY
    # =========================================================

    bedrooms: int

    bathrooms: int

    property_type: str

    area_sqft: Optional[float] = None

    # =========================================================
    # FEATURES
    # =========================================================

    furnished: Optional[str] = None

    parking: Optional[bool] = None

    garden: Optional[bool] = None

    balcony: Optional[bool] = None

    terrace: Optional[bool] = None

    # =========================================================
    # IMPORTANT / UNIQUE FEATURES
    # =========================================================

    highlights: List[str] = Field(
        default_factory=list,
        description=(
            "Important and distinctive property features "
            "from the database that are useful to mention "
            "to the buyer or renter."
        ),
    )

    # =========================================================
    # FRONTEND
    # =========================================================

    property_url: HttpUrl

    image_url: Optional[HttpUrl] = None

    # =========================================================
    # MATCHING
    # =========================================================

    match_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="AI relevance score",
    )


class PropertySearchResponse(BaseModel):
    """Response returned by the search tool."""

    total_matches: int

    properties: List[MatchedProperty]