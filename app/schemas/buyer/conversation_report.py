from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# -------------------------
# Contact
# -------------------------

class ContactInformation(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


# -------------------------
# Preferences
# -------------------------

class BuyerPreferences(BaseModel):
    city: Optional[str] = None
    locality: Optional[str] = None

    property_type: Optional[str] = None
    listing_type: Optional[str] = None

    min_budget: Optional[float] = None
    max_budget: Optional[float] = None

    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None

    min_area_sqft: Optional[float] = None
    max_area_sqft: Optional[float] = None

    amenities: List[str] = Field(default_factory=list)

    financing_type: Optional[str] = None

    move_in_timeline: Optional[str] = None

    first_time_buyer: Optional[bool] = None


# -------------------------
# Properties
# -------------------------

class PropertyInterest(BaseModel):
    property_id: str

    interest_level: str

    liked_reason: Optional[str] = None

    concerns: List[str] = Field(default_factory=list)

    questions_asked: List[str] = Field(default_factory=list)


# -------------------------
# Viewing
# -------------------------

class ViewingInformation(BaseModel):
    scheduled: bool = False

    viewing_id: Optional[str] = None

    property_id: Optional[str] = None

    scheduled_at: Optional[datetime] = None

    agent_id: Optional[str] = None


# -------------------------
# Insights
# -------------------------

class ConversationInsights(BaseModel):
    summary: str

    buyer_intent: str

    sentiment: str

    urgency: str

    buying_stage: str

    buying_signals: List[str] = Field(default_factory=list)

    negative_signals: List[str] = Field(default_factory=list)

    objections: List[str] = Field(default_factory=list)

    pain_points: List[str] = Field(default_factory=list)

    motivations: List[str] = Field(default_factory=list)

    follow_up_actions: List[str] = Field(default_factory=list)

    recommended_next_action: Optional[str] = None


# -------------------------
# Lead
# -------------------------

class LeadQualification(BaseModel):
    qualified: bool

    lead_score: int = Field(ge=0, le=100)

    priority: str

    qualification_reason: str


# -------------------------
# Metadata
# -------------------------

class ConversationMetadata(BaseModel):
    total_properties_discussed: int = 0

    total_properties_liked: int = 0

    viewing_requested: bool = False

    contact_information_collected: bool = False


# -------------------------
# Root
# -------------------------

class ConversationReport(BaseModel):
    session_id: str

    completed_at: datetime

    contact: ContactInformation

    preferences: BuyerPreferences

    interested_properties: List[PropertyInterest] = Field(default_factory=list)

    viewing: Optional[ViewingInformation] = None

    insights: ConversationInsights

    qualification: LeadQualification

    metadata: ConversationMetadata