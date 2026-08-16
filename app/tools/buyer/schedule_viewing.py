import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.crud.viewing import viewing_repo
from app.db.crud.buyer import buyer_repo
from app.schemas.buyer.viewing import (
    ScheduleViewingRequest,
    ScheduleViewingResponse,
)


def schedule_viewing(
    db: Session,
    request: ScheduleViewingRequest,
) -> ScheduleViewingResponse:
    """
    Schedule a property viewing for a buyer.
    """
    # 1. Ensure we have a valid target datetime
    target_dt = request.preferred_datetime or datetime.utcnow()
    target_date = target_dt.date()
    target_time = target_dt.time()

    # 2. Find or create a buyer lead using phone or name
    buyer_id = None
    if request.phone_number:
        existing_buyer = buyer_repo.get_by_phone(db=db, phone=request.phone_number)
        if existing_buyer:
            buyer_id = existing_buyer.id

    if not buyer_id:
        new_buyer = buyer_repo.create_buyer(
            db=db,
            name=request.buyer_name or "Anonymous Buyer",
            phone=request.phone_number,
            email=request.email,
        )
        buyer_id = new_buyer.id

    # 3. Create viewing record matching the ORM model (viewing_date & viewing_time)
    viewing = viewing_repo.schedule_viewing(
        db=db,
        property_id=uuid.UUID(request.property_id) if isinstance(request.property_id, str) else request.property_id,
        buyer_lead_id=buyer_id,  # 👈 Matches Viewing model column
        viewing_date=target_date, # 👈 Matches Viewing model column
        viewing_time=target_time, # 👈 Matches Viewing model column
        notes=request.notes,
        status="Booked",
    )

    # 4. Return matching ScheduleViewingResponse schema
    return ScheduleViewingResponse(
        success=True,
        viewing_id=str(viewing.id),
        property_id=str(viewing.property_id),
        scheduled_datetime=target_dt,
        message=f"Viewing successfully scheduled for {target_dt.strftime('%B %d, %Y at %I:%M %p')}.",
    )