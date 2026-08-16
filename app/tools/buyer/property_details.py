from sqlalchemy.orm import Session

from app.db.crud.property import property_repo

from app.schemas.buyer.property_details import (
    PropertyDetailsRequest,
    PropertyDetailsResponse,
)

# Cap the number of images forwarded for a single property's full detail
# view. Scraped listings can carry 10-15+ photos; this keeps the payload
# sent over the WebRTC data channel reasonable while still giving the
# frontend enough for a proper gallery.
MAX_IMAGES_PER_PROPERTY = 12


def get_property_details(
    db: Session,
    request: PropertyDetailsRequest,
) -> PropertyDetailsResponse:
    """
    Fetch complete details for a single property.
    """

    property_obj = property_repo.get_property(
        db=db,
        property_id=request.property_id,
    )

    if property_obj is None:

        raise ValueError(
            f"Property '{request.property_id}' not found."
        )

    # ------------------------------------------------------
    # Convert JSONB image list into response URLs
    # ------------------------------------------------------

    image_urls = []

    if property_obj.image_urls:

        for image in property_obj.image_urls:

            if image:

                image_urls.append(
                    image
                )

    image_urls = image_urls[:MAX_IMAGES_PER_PROPERTY]

    # ------------------------------------------------------
    # Convert ORM -> Pydantic response
    # ------------------------------------------------------

    return PropertyDetailsResponse(

        property_id=str(
            property_obj.id
        ),

        source=property_obj.source,

        title=property_obj.title,

        description=(
            property_obj.description
        ),

        price=property_obj.price,

        currency=(
            property_obj.currency
            or "GBP"
        ),

        price_period=(
            property_obj.price_period
        ),

        property_type=(
            property_obj.property_type
            or "Property"
        ),

        listing_type=(
            property_obj.listing_type
            or "sale"
        ),

        status=(
            property_obj.status
        ),

        address=(
            property_obj.address
        ),

        city=(
            property_obj.city
        ),

        locality=(
            property_obj.locality
        ),

        postcode=(
            property_obj.postcode
        ),

        bedrooms=(
            property_obj.bedrooms
        ),

        bathrooms=(
            property_obj.bathrooms
        ),

        reception_rooms=(
            property_obj.reception_rooms
        ),

        area_sqft=(
            float(property_obj.area_sqft)
            if property_obj.area_sqft is not None
            else None
        ),

        furnished=(
            property_obj.furnished
        ),

        parking=(
            property_obj.parking
        ),

        parking_spaces=(
            property_obj.parking_spaces
        ),

        garden=(
            property_obj.garden
        ),

        garage=(
            property_obj.garage
        ),

        balcony=(
            property_obj.balcony
        ),

        terrace=(
            property_obj.terrace
        ),

        pets_allowed=(
            property_obj.pets_allowed
        ),

        tenure=(
            property_obj.tenure
        ),

        epc_rating=(
            property_obj.epc_rating
        ),

        amenities=(
            property_obj.amenities
            or []
        ),

        image_urls=image_urls,

        agent_name=(
            property_obj.agent_name
        ),

        available_from=(
            property_obj.available_from
        ),

        property_url=(
            property_obj.listing_url
        ),
    )