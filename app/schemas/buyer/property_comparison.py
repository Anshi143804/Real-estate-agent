"""
Schemas for the compare_properties tool.
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class PropertyComparisonRequest(BaseModel):
    """Request to compare two or more properties."""

    property_ids: List[str] = Field(
        ...,
        min_length=2,
        description="Two or more property IDs to compare"
    )


class ComparedProperty(BaseModel):
    """Comparable attributes of a property."""

    property_id: str

    title: str

    price: Decimal

    currency: str = "GBP"

    price_period: Optional[str] = None

    property_type: str

    location: str

    postcode: Optional[str] = None

    bedrooms: Optional[int] = None

    bathrooms: Optional[int] = None

    reception_rooms: Optional[int] = None

    area_sqft: Optional[float] = None

    furnished: Optional[str] = None

    parking: Optional[bool] = None

    parking_spaces: Optional[int] = None

    garden: Optional[bool] = None

    garage: Optional[bool] = None

    balcony: Optional[bool] = None

    terrace: Optional[bool] = None

    pets_allowed: Optional[bool] = None

    tenure: Optional[str] = None

    epc_rating: Optional[str] = None

    image_urls: List[HttpUrl] = Field(
        default_factory=list
    )

    property_url: HttpUrl


class PropertyComparisonResponse(BaseModel):
    """Comparison result returned to the AI."""

    properties: List[ComparedProperty]

    summary: str