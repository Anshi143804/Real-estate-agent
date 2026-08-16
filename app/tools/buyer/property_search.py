from sqlalchemy.orm import Session

from app.schemas.buyer.property_search import (
    PropertySearchRequest,
    PropertySearchResponse,
    MatchedProperty,
)

from app.db.crud.property import property_repo


def build_property_highlights(p) -> list[str]:
    """
    Build important and distinctive property highlights using
    only information that actually exists in the database.
    """

    highlights: list[str] = []

    if p.area_sqft:
        highlights.append(f"{float(p.area_sqft):,.0f} sq ft")

    if p.reception_rooms:

        highlights.append(
            f"{p.reception_rooms} reception room"
            + (
                "s"
                if p.reception_rooms != 1
                else ""
            )
        )

    if p.parking:
        if p.parking_spaces:
            highlights.append(f"{p.parking_spaces} parking spaces")
        else:
            highlights.append("Parking")

    if p.garage:
        highlights.append("Garage")

    if p.garden:
        highlights.append("Garden")

    if p.balcony:
        highlights.append("Balcony")

    if p.terrace:
        highlights.append("Terrace")

    if p.furnished:
        highlights.append(p.furnished.replace("_", " ").title())

    if p.pets_allowed is True:
        highlights.append("Pets allowed")

    if p.tenure:
        highlights.append(p.tenure.title())

    if p.epc_rating:
        highlights.append(f"EPC {p.epc_rating.upper()}")

    if p.amenities:
        for amenity in p.amenities:
            if not amenity:
                continue
            amenity = str(amenity).strip()
            if not amenity:
                continue

            if not any(
                amenity.lower() == existing.lower()
                for existing in highlights
            ):
                highlights.append(amenity)

    return highlights[:6]


def find_matching_properties(
    db: Session,
    request: PropertySearchRequest,
) -> PropertySearchResponse:
    """Search for properties matching the buyer/renter's requirements."""

    properties = property_repo.search(
        db=db,
        city=request.city,
        locality=request.locality,

        property_type=request.property_type,

        listing_type=request.listing_type,

        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        min_price=request.min_budget,

        max_price=request.max_budget,

        # ----------------------------------------------------
        # ROOMS
        # ----------------------------------------------------

        bedrooms=request.min_bedrooms,

        bathrooms=request.min_bathrooms,

        reception_rooms=request.min_reception_rooms,

        # ----------------------------------------------------
        # PROPERTY SIZE
        # ----------------------------------------------------

        min_area_sqft=request.min_area_sqft,

        max_area_sqft=request.max_area_sqft,

        # ----------------------------------------------------
        # PROPERTY FEATURES
        # ----------------------------------------------------

        furnished=request.furnished,

        parking=request.parking,

        garden=request.garden,

        garage=request.garage,

        balcony=request.balcony,

        terrace=request.terrace,

        pets_allowed=request.pets_allowed,

        tenure=request.tenure,

        # ----------------------------------------------------
        # ONLY AVAILABLE LISTINGS
        # ----------------------------------------------------

        status="available",
    )

    # ========================================================
    # CONVERT DATABASE OBJECTS TO RESPONSE OBJECTS
    # ========================================================

    matched_properties: list[MatchedProperty] = []

    for p in properties:

        # ----------------------------------------------------
        # BUILD LOCATION
        # ----------------------------------------------------

        location_parts = [p.locality, p.city]
        location = ", ".join(part for part in location_parts if part)
        if not location:
            location = p.address or "Unknown location"

        image_url = None
        if p.image_urls and isinstance(p.image_urls, list) and len(p.image_urls) > 0:
            image_url = p.image_urls[0]

        highlights = build_property_highlights(p)

        matched_properties.append(
            MatchedProperty(
                property_id=str(p.id),
                title=p.title,
                price=p.price,
                currency=p.currency or "GBP",
                price_period=p.price_period,
                location=location,
                postcode=p.postcode,
                bedrooms=p.bedrooms or 0,
                bathrooms=p.bathrooms or 0,
                property_type=p.property_type or "Property",
                area_sqft=float(p.area_sqft) if p.area_sqft is not None else None,

                furnished=p.furnished,

                parking=p.parking,

                garden=p.garden,

                balcony=p.balcony,

                terrace=p.terrace,

                highlights=highlights,
                property_url=p.listing_url,
                image_url=image_url,
                match_score=1.0,
            )
        )

    return PropertySearchResponse(
        total_matches=len(matched_properties),
        properties=matched_properties,
    )