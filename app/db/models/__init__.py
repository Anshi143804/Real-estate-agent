"""
app/db/models/__init__.py

Import all models so SQLAlchemy can discover them for table creation.
"""

from app.db.models.buyer import BuyerLead
from app.db.models.seller import SellerLead
from app.db.models.property import Property
from app.db.models.viewing import Viewing
from app.db.models.valuation import Valuation
from app.db.models.conversation import ConversationSession, ConversationMessage
from app.db.models.evaluation import ConversationEvaluation

__all__ = [
    "BuyerLead",
    "SellerLead",
    "Property",
    "Viewing",
    "Valuation",
    "ConversationSession",
    "ConversationMessage",
    "ConversationEvaluation",
]
