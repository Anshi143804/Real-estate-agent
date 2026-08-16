from typing import List

from sqlalchemy.orm import Session

from app.schemas.buyer.property_comparison import (
    PropertyComparisonRequest,
    PropertyComparisonResponse,
    ComparedProperty,
)

from app.db.crud.property import property_repo

# Cap the number of images we forward per property so a comparison of
# several properties (each of which may have 10-15 scraped images) doesn't
# blow up the payload sent down the WebRTC data channel.
MAX_IMAGES_PER_PROPERTY = 8


def compare_properties(
    db: Session,
    request: PropertyComparisonRequest,
) -> PropertyComparisonResponse:
    """
    Fetch multiple properties and compare
    their important attributes.
    """

    compared_list: List[ComparedProperty] = []

    for prop_id in request.property_ids:

        p = property_repo.get_property(
            db,
            property_id=prop_id,
        )

        if not p:
            continue

        # --------------------------------------------------
        # LOCATION
        # --------------------------------------------------

        location_parts = [
            p.locality,
            p.city,
        ]

        location = ", ".join(
            part
            for part in location_parts
            if part
        )

        if not location:
            location = p.address or "Unknown location"

        # --------------------------------------------------
        # IMAGES
        # --------------------------------------------------

        image_urls = [
            image
            for image in (p.image_urls or [])
            if image
        ][:MAX_IMAGES_PER_PROPERTY]

        # --------------------------------------------------
        # CREATE COMPARISON OBJECT
        # --------------------------------------------------

        compared_item = ComparedProperty(

            property_id=str(p.id),

            title=p.title,

            price=p.price,

            currency=p.currency or "GBP",

            price_period=p.price_period,

            property_type=(
                p.property_type
                or "Property"
            ),

            location=location,

            postcode=p.postcode,

            bedrooms=p.bedrooms,

            bathrooms=p.bathrooms,

            reception_rooms=p.reception_rooms,

            area_sqft=(
                float(p.area_sqft)
                if p.area_sqft is not None
                else None
            ),

            furnished=p.furnished,

            parking=p.parking,

            parking_spaces=p.parking_spaces,

            garden=p.garden,

            garage=p.garage,

            balcony=p.balcony,

            terrace=p.terrace,

            pets_allowed=p.pets_allowed,

            tenure=p.tenure,

            epc_rating=p.epc_rating,

            image_urls=image_urls,

            property_url=p.listing_url,
        )

        compared_list.append(
            compared_item
        )

    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    summary_parts = []

    for p in compared_list:

        price_text = (
            f"£{p.price:,.0f}"
            if p.price is not None
            else "Price unavailable"
        )

        beds = (
            p.bedrooms
            if p.bedrooms is not None
            else "?"
        )

        baths = (
            p.bathrooms
            if p.bathrooms is not None
            else "?"
        )

        summary_parts.append(
            f"{p.title}: "
            f"{price_text} "
            f"({beds} beds, "
            f"{baths} baths)"
        )

    summary_text = (
        "Comparison: "
        + " VS ".join(
            summary_parts
        )
    )

    return PropertyComparisonResponse(
        properties=compared_list,
        summary=summary_text,
    )