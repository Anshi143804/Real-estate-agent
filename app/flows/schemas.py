from pipecat.flows import FlowsFunctionSchema
from .handlers import (
    proceed_to_requirements_handler,
    property_search_handler,
    property_details_handler,
    property_comparison_handler,
    schedule_viewing_handler,
    conversation_analysis_handler,
    finalize_conversation_handler,
)

# ---------------------------------------------------------------------
# 0. Initial Transition Schema (greeting -> requirements)
# ---------------------------------------------------------------------
proceed_to_requirements_schema = FlowsFunctionSchema(
    name="proceed_to_requirements_handler",
    description="Call this tool immediately after asking the user what kind of property they are looking for (rent/buy). Moves the conversation flow state to requirements collection.",
    properties={},
    required=[],
    handler=proceed_to_requirements_handler,
)

# ---------------------------------------------------------------------
# 1. Property Search Schema
# ---------------------------------------------------------------------
property_search_schema = FlowsFunctionSchema(
    name="property_search_handler",

    description=(
        "Search the real estate database for properties matching "
        "the buyer's requirements. Use this tool once enough "
        "requirements are known. Include only criteria the buyer "
        "actually specified."
    ),

    properties={

        "city": {
            "type": "string",
            "description": "Target city, e.g. London",
        },

        "locality": {
            "type": "string",
            "description": "Neighborhood, district, or locality",
        },

        "listing_type": {
            "type": "string",
            "enum": ["buy", "rent"],
            "description": "Whether the user wants to buy or rent",
        },

        "property_type": {
            "type": "string",
            "description": (
                "Property type such as apartment, flat, house, "
                "detached house, terraced house, villa, studio"
            ),
        },

        "bedrooms": {
            "type": "integer",
            "description": "Minimum number of bedrooms",
        },

        "bathrooms": {
            "type": "integer",
            "description": "Minimum number of bathrooms",
        },

        "reception_rooms": {
            "type": "integer",
            "description": "Minimum number of reception rooms",
        },

        "budget_min": {
            "type": "number",
            "description": "Minimum budget",
        },

        "budget_max": {
            "type": "number",
            "description": "Maximum purchase price or rent",
        },

        "min_area_sqft": {
            "type": "number",
            "description": "Minimum property size in square feet",
        },

        "max_area_sqft": {
            "type": "number",
            "description": "Maximum property size in square feet",
        },

        "furnished": {
            "type": "string",
            "description": (
                "Furnished, unfurnished, or part-furnished"
            ),
        },

        "parking": {
            "type": "boolean",
            "description": "Whether parking is required",
        },

        "garden": {
            "type": "boolean",
            "description": "Whether a garden is required",
        },

        "garage": {
            "type": "boolean",
            "description": "Whether a garage is required",
        },

        "balcony": {
            "type": "boolean",
            "description": "Whether a balcony is required",
        },

        "terrace": {
            "type": "boolean",
            "description": "Whether a terrace is required",
        },

        "pets_allowed": {
            "type": "boolean",
            "description": "Whether pets must be allowed",
        },

        "tenure": {
            "type": "string",
            "description": "Freehold or leasehold",
        },

        "features": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": (
                "Additional requirements such as fireplace, "
                "utility room, period features, etc."
            ),
        },
    },

    required=[
        "city",
        "listing_type",
    ],

    handler=property_search_handler,
)

# ---------------------------------------------------------------------
# 2. Property Details Schema
# ---------------------------------------------------------------------
property_details_schema = FlowsFunctionSchema(
    name="property_details_handler",
    description="Fetch full specifications, exact pricing, floor plans, and amenities for a specific property by its ID.",
    properties={
        "property_id": {
            "type": "string",
            "description": "Unique identifier of the property (e.g., 'PROP-101')."
        }
    },
    required=["property_id"],
    handler=property_details_handler,
)

# ---------------------------------------------------------------------
# 3. Property Comparison Schema
# ---------------------------------------------------------------------
property_comparison_schema = FlowsFunctionSchema(
    name="property_comparison_handler",
    description="Compare two or more properties side by side based on price, bedrooms, locality, amenities, and pros/cons.",
    properties={
        "property_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of property IDs to compare (e.g., ['PROP-101', 'PROP-102'])."
        }
    },
    required=["property_ids"],
    handler=property_comparison_handler,
)

# ---------------------------------------------------------------------
# 4. Schedule Viewing Schema
# ---------------------------------------------------------------------
# app/flows/schemas.py

schedule_viewing_schema = FlowsFunctionSchema(
    name="schedule_viewing_handler",
    description="Schedules a property viewing ONLY AFTER collecting the buyer's full name, phone number, preferred date, and preferred time.",
    properties={
        "property_id": {
            "type": "string",
            "description": "The unique property ID"
        },
        "buyer_name": {
            "type": "string",
            "description": "Full name of the buyer"
        },
        "phone_number": {
            "type": "string",
            "description": "Contact phone number of the buyer"
        },
        "email": {
            "type": "string",
            "description": "Optional email address"
        },
        "preferred_date": {
            "type": "string",
            "description": "Preferred viewing date (YYYY-MM-DD)"
        },
        "preferred_time": {
            "type": "string",
            "description": "Preferred viewing time (HH:MM)"
        }
    },
    required=["property_id", "buyer_name", "phone_number", "preferred_date", "preferred_time"],
    handler=schedule_viewing_handler,
)

# ---------------------------------------------------------------------
# 5. Conversation Analysis Schema
# ---------------------------------------------------------------------
conversation_analysis_schema = FlowsFunctionSchema(
    name="conversation_analysis_handler",
    description="Generate a structured CRM analysis report at the end of the conversation.",
    properties={},
    required=[],
    handler=conversation_analysis_handler,
)


finalize_conversation_schema = FlowsFunctionSchema(
    name="finalize_conversation_handler",
    description="Save the conversation CRM report to the database and terminate the voice call.",
    properties={},
    required=[],
    handler=finalize_conversation_handler,
)