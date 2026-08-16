"""
Schemas for the get_property_details tool.
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class PropertyDetailsRequest(BaseModel):
    property_id: str


class PropertyDetailsResponse(BaseModel):

    property_id: str

    source: Optional[str] = None

    title: str

    description: Optional[str] = None

    price: Decimal

    currency: str = "GBP"

    price_period: Optional[str] = None

    property_type: str

    listing_type: str

    status: Optional[str] = None

    address: Optional[str] = None

    city: Optional[str] = None

    locality: Optional[str] = None

    postcode: Optional[str] = None


    bedrooms: Optional[int] = None

    bathrooms: Optional[int] = None

    reception_rooms: Optional[int] = None

    area_sqft: Optional[float] = None


    furnished: Optional[str] = None

    parking: bool = False

    parking_spaces: Optional[int] = None

    garden: bool = False

    garage: bool = False

    balcony: bool = False

    terrace: bool = False

    pets_allowed: Optional[bool] = None

    tenure: Optional[str] = None

    epc_rating: Optional[str] = None


    amenities: List[str] = Field(
        default_factory=list
    )

    image_urls: List[HttpUrl] = Field(
        default_factory=list
    )


    agent_name: Optional[str] = None


    available_from: Optional[str] = None


    property_url: HttpUrl