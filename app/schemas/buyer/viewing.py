"""
Schemas for the schedule_viewing tool.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class ScheduleViewingRequest(BaseModel):
    """Request to schedule a property viewing."""

    property_id: str

    buyer_name: Optional[str] = None

    phone_number: Optional[str] = None

    email: Optional[EmailStr] = None

    preferred_date: Optional[str] = None
    
    preferred_time: Optional[str] = None

    preferred_datetime: Optional[datetime] = None

    notes: Optional[str] = Field(
        default=None,
        description="Additional notes or buyer preferences"
    )

    @model_validator(mode="before")
    def parse_and_combine_datetime(cls, values):
        if not isinstance(values, dict):
            return values

        pref_datetime = values.get("preferred_datetime")
        pref_date = values.get("preferred_date")
        pref_time = values.get("preferred_time", "12:00")

        # 1. If LLM passed preferred_date and preferred_time, combine them
        if pref_date and not pref_datetime:
            combined_str = f"{pref_date} {pref_time}"
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %I:%M %p"):
                try:
                    values["preferred_datetime"] = datetime.strptime(combined_str, fmt)
                    break
                except ValueError:
                    pass

        # 2. If preferred_datetime was passed as a string, parse it into datetime
        elif isinstance(pref_datetime, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    values["preferred_datetime"] = datetime.strptime(pref_datetime, fmt)
                    break
                except ValueError:
                    pass

        # 3. Fallback: if no valid datetime could be parsed, set default
        if not values.get("preferred_datetime"):
            values["preferred_datetime"] = datetime.utcnow()

        return values


class ScheduleViewingResponse(BaseModel):
    """Response returned after scheduling a viewing."""

    success: bool

    viewing_id: str

    property_id: str

    scheduled_datetime: datetime

    message: str