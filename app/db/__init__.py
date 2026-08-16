"""
Import all SQLAlchemy models.

This ensures SQLAlchemy discovers every model before
Base.metadata.create_all() is called.
"""

from .models.property import Property
from .models.buyer import BuyerLead
from .models.seller import SellerLead
from .models.viewing import Viewing
from .models.valuation import Valuation
from .models.conversation import (
    ConversationSession,
    ConversationMessage,
)

__all__ = [
    "Property",
    "BuyerLead",
    "SellerLead",
    "Viewing",
    "Valuation",
    "ConversationSession",
    "ConversationMessage",
]