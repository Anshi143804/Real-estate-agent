"""
Schemas for the save_lead_summary tool.
"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr


class LeadSummaryRequest(BaseModel):
    """Lead summary generated after the buyer conversation."""

    buyer_name: Optional[str] = None

    phone_number: Optional[str] = None

    email: Optional[EmailStr] = None

    summary: str

    interested_property_ids: List[str] = []

    viewing_scheduled: bool = False

    notes: Optional[str] = None


class LeadSummaryResponse(BaseModel):
    """Response after saving the lead summary."""

    success: bool

    lead_id: str

    message: str