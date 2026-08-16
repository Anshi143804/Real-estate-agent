"""
Central registry for all AI tools.
"""

from app.tools.buyer.finalise_conversation import ConversationSummaryTool
from app.tools.buyer.property_comparison import PropertyComparisonTool
from app.tools.buyer.property_details import PropertyDetailsTool
from app.tools.buyer.property_search import PropertySearchTool
from app.tools.buyer.schedule_viewing import ScheduleViewingTool


BUYER_TOOLS = [
    PropertySearchTool(),
    PropertyDetailsTool(),
    PropertyComparisonTool(),
    ScheduleViewingTool(),
    ConversationSummaryTool(),
]


TOOL_REGISTRY = {
    tool.name: tool
    for tool in BUYER_TOOLS
}