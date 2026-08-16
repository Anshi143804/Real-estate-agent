from sqlalchemy.orm import Session

from app.schemas.buyer.property_search import (
    PropertySearchRequest,
    PropertySearchResponse,
    MatchedProperty,
)

from app.db.crud.property import property_repo


# ============================================================
# PROPERTY HIGHLIGHTS
# ============================================================

def build_property_highlights(p) -> list[str]:
    """
    Build important and distinctive property highlights using
    only information that actually exists in the database.

    These highlights are intended to be used by:
        - the frontend property card
        - the AI voice agent

    No property features are invented.
    """

    highlights: list[str] = []

    # --------------------------------------------------------
    # PROPERTY SIZE
    # --------------------------------------------------------

    if p.area_sqft:

        highlights.append(
            f"{float(p.area_sqft):,.0f} sq ft"
        )

    # --------------------------------------------------------
    # RECEPTION ROOMS
    # --------------------------------------------------------

    if p.reception_rooms:

        highlights.append(
            f"{p.reception_rooms} reception room"
            + (
                "s"
                if p.reception_rooms != 1
                else ""
            )
        )

    # --------------------------------------------------------
    # PARKING
    # --------------------------------------------------------

    if p.parking:

        if p.parking_spaces:

            highlights.append(
                f"{p.parking_spaces} parking spaces"
            )

        else:

            highlights.append(
                "Parking"
            )

    # --------------------------------------------------------
    # GARAGE
    # --------------------------------------------------------

    if p.garage:

        highlights.append(
            "Garage"
        )

    # --------------------------------------------------------
    # GARDEN
    # --------------------------------------------------------

    if p.garden:

        highlights.append(
            "Garden"
        )

    # --------------------------------------------------------
    # BALCONY
    # --------------------------------------------------------

    if p.balcony:

        highlights.append(
            "Balcony"
        )

    # --------------------------------------------------------
    # TERRACE
    # --------------------------------------------------------

    if p.terrace:

        highlights.append(
            "Terrace"
        )

    # --------------------------------------------------------
    # FURNISHED
    # --------------------------------------------------------

    if p.furnished:

        highlights.append(
            p.furnished
            .replace("_", " ")
            .title()
        )

    # --------------------------------------------------------
    # PETS
    # --------------------------------------------------------

    if p.pets_allowed is True:

        highlights.append(
            "Pets allowed"
        )

    # --------------------------------------------------------
    # TENURE
    # --------------------------------------------------------

    if p.tenure:

        highlights.append(
            p.tenure.title()
        )

    # --------------------------------------------------------
    # EPC
    # --------------------------------------------------------

    if p.epc_rating:

        highlights.append(
            f"EPC {p.epc_rating.upper()}"
        )

    # --------------------------------------------------------
    # AMENITIES
    # --------------------------------------------------------

    if p.amenities:

        for amenity in p.amenities:

            if not amenity:
                continue

            amenity = str(
                amenity
            ).strip()

            if not amenity:
                continue

            # Avoid duplicate highlights
            if not any(
                amenity.lower()
                == existing.lower()
                for existing in highlights
            ):

                highlights.append(
                    amenity
                )

    # --------------------------------------------------------
    # LIMIT NUMBER OF HIGHLIGHTS
    # --------------------------------------------------------

    return highlights[:6]


# ============================================================
# FIND MATCHING PROPERTIES
# ============================================================

def find_matching_properties(
    db: Session,
    request: PropertySearchRequest,
) -> PropertySearchResponse:
    """
    Search for properties matching the buyer/renter's
    requirements.
    """

    # ========================================================
    # SEARCH DATABASE
    # ========================================================

    properties = property_repo.search(
        db=db,

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        city=request.city,

        locality=request.locality,

        # ----------------------------------------------------
        # PROPERTY TYPE
        # ----------------------------------------------------

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

            location = (
                p.address
                or "Unknown location"
            )

        # ----------------------------------------------------
        # FIRST IMAGE
        # ----------------------------------------------------

        image_url = None

        if p.image_urls:

            if (
                isinstance(
                    p.image_urls,
                    list,
                )
                and len(p.image_urls) > 0
            ):

                image_url = p.image_urls[0]

        # ----------------------------------------------------
        # BUILD HIGHLIGHTS
        # ----------------------------------------------------

        highlights = (
            build_property_highlights(p)
        )

        # ----------------------------------------------------
        # CREATE MATCHED PROPERTY
        # ----------------------------------------------------

        matched_properties.append(
            MatchedProperty(

                # ------------------------------------------------
                # INTERNAL IDENTIFIER
                # ------------------------------------------------

                property_id=str(
                    p.id
                ),

                # ------------------------------------------------
                # BASIC INFORMATION
                # ------------------------------------------------

                title=p.title,

                price=p.price,

                currency=(
                    p.currency
                    or "GBP"
                ),

                price_period=(
                    p.price_period
                ),

                # ------------------------------------------------
                # LOCATION
                # ------------------------------------------------

                location=location,

                postcode=p.postcode,

                # ------------------------------------------------
                # ROOMS
                # ------------------------------------------------

                bedrooms=(
                    p.bedrooms
                    or 0
                ),

                bathrooms=(
                    p.bathrooms
                    or 0
                ),

                # ------------------------------------------------
                # PROPERTY TYPE
                # ------------------------------------------------

                property_type=(
                    p.property_type
                    or "Property"
                ),

                # ------------------------------------------------
                # SIZE
                # ------------------------------------------------

                area_sqft=(
                    float(p.area_sqft)
                    if p.area_sqft is not None
                    else None
                ),

                # ------------------------------------------------
                # FEATURES
                # ------------------------------------------------

                furnished=p.furnished,

                parking=p.parking,

                garden=p.garden,

                balcony=p.balcony,

                terrace=p.terrace,

                # ------------------------------------------------
                # IMPORTANT / UNIQUE FEATURES
                # ------------------------------------------------

                highlights=highlights,

                # ------------------------------------------------
                # FRONTEND ONLY
                #
                # Keep these in the structured response so the
                # frontend can display them.
                #
                # Nova should NOT read these aloud.
                # ------------------------------------------------

                property_url=(
                    p.listing_url
                ),

                image_url=image_url,

                # ------------------------------------------------
                # MATCH SCORE
                #
                # Currently every result gets 1.0.
                # We can implement real scoring later.
                # ------------------------------------------------

                match_score=1.0,
            )
        )

    # ========================================================
    # RETURN SEARCH RESPONSE
    # ========================================================

    return PropertySearchResponse(

        total_matches=len(
            matched_properties
        ),

        properties=matched_properties,
    )