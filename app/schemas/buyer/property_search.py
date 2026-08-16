from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class PropertySearchRequest(BaseModel):

    city: str = Field(
        ...,
        description="Preferred city",
    )

    locality: Optional[str] = Field(
        default=None,
        description="Preferred locality, neighborhood, or area",
    )

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

    min_budget: Optional[Decimal] = Field(
        default=None,
        description="Minimum purchase price or monthly rent",
    )

    max_budget: Optional[Decimal] = Field(
        default=None,
        description="Maximum purchase price or monthly rent",
    )

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

    min_area_sqft: Optional[float] = Field(
        default=None,
        description="Minimum property size in square feet",
    )

    max_area_sqft: Optional[float] = Field(
        default=None,
        description="Maximum property size in square feet",
    )

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

    tenure: Optional[str] = Field(
        default=None,
        description="Freehold or leasehold",
    )

    features: List[str] = Field(
        default_factory=list,
        description=(
            "Additional requirements such as fireplace, "
            "utility room, period features, double glazing, "
            "south-facing garden, etc."
        ),
    )


class MatchedProperty(BaseModel):

    property_id: str

    title: str

    price: Decimal

    currency: str = "GBP"

    price_period: Optional[str] = None

    location: str

    postcode: Optional[str] = None

    bedrooms: int

    bathrooms: int

    property_type: str

    area_sqft: Optional[float] = None

    furnished: Optional[str] = None

    parking: Optional[bool] = None

    garden: Optional[bool] = None

    balcony: Optional[bool] = None

    terrace: Optional[bool] = None

    highlights: List[str] = Field(
        default_factory=list,
        description=(
            "Important and distinctive property features "
            "from the database that are useful to mention "
            "to the buyer or renter."
        ),
    )

    property_url: HttpUrl

    image_url: Optional[HttpUrl] = None

    match_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="AI relevance score",
    )


class PropertySearchResponse(BaseModel):

    total_matches: int

    properties: List[MatchedProperty]