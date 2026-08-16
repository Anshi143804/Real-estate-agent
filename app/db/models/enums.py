from enum import Enum


class LeadStatus(str, Enum):
    NEW = "New"
    QUALIFIED = "Qualified"
    VIEWING_BOOKED = "Viewing Booked"
    VALUATION_BOOKED = "Valuation Booked"
    CLOSED = "Closed"


class ListingStatus(str, Enum):
    AVAILABLE = "Available"
    UNDER_OFFER = "Under Offer"
    SOLD = "Sold"


class ListingType(str, Enum):
    SALE = "Sale"
    RENT = "Rent"


class PropertyType(str, Enum):
    HOUSE = "House"
    APARTMENT = "Apartment"
    FLAT = "Flat"
    BUNGALOW = "Bungalow"
    MAISONETTE = "Maisonette"
    PENTHOUSE = "Penthouse"


class ViewingStatus(str, Enum):
    BOOKED = "Booked"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class ConversationSpeaker(str, Enum):
    USER = "User"
    ASSISTANT = "Assistant"