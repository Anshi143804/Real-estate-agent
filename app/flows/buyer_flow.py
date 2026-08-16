from pipecat.flows import (
    ContextStrategy,
    ContextStrategyConfig,
    NodeConfig,
)

from .schemas import (
    proceed_to_requirements_schema,
    property_search_schema,
    property_details_schema,
    property_comparison_schema,
    schedule_viewing_schema,
    conversation_analysis_schema,
    finalize_conversation_schema,
)

from .prompts import (
    GREETING_PROMPT,
    REQUIREMENTS_PROMPT,
    PROPERTY_DISCUSSION_PROMPT,
    COMPARISON_PROMPT,
    VIEWING_PROMPT,
    CLOSING_PROMPT,
    FINALIZE_PROMPT,
)


ROLE_MESSAGE = """
You are Nova, an experienced real estate consultant speaking with a buyer on a live phone call.

Your job is to help buyers discover suitable properties, answer questions, compare listings, schedule viewings, and collect buyer information naturally.

VOICE STYLE (applies to every response, always):
- This is a spoken phone call, not a chat window. Speak in short, natural sentences the way a person would on the phone.
- The buyer's screen already shows a rich card for every property mentioned (price, address, beds/baths, a link) - never say a property ID, listing ID, or URL out loud, and never speak in markdown (no asterisks, bullet points, or "[text](link)").
- Be concise: one or two sentences is usually enough. Don't repeat information you already said earlier in the call.
- Never say the same greeting or question more than once in a row.

Never invent property information or pricing.
Always use tools whenever searching for properties, comparing listings, scheduling viewings, or transitioning conversational state.
"""


def greeting_node() -> NodeConfig:
    return {
        "name": "greeting",
        "role_message": ROLE_MESSAGE,
        "task_messages": [
            {
                "role": "system",
                "content": GREETING_PROMPT,
            }
        ],
        "functions": [
            proceed_to_requirements_schema,
            property_search_schema,
        ],
        "context_strategy": ContextStrategyConfig(
    strategy=ContextStrategy.RESET
) ,
        "respond_immediately": True,
    }


def requirements_node() -> NodeConfig:
    return {
        "name": "requirements",
        "role_message": ROLE_MESSAGE,
        "task_messages": [
            {
                "role": "system",
                "content": REQUIREMENTS_PROMPT,
            }
        ],
        "functions": [
            property_search_schema,
        ],
        "context_strategy": ContextStrategyConfig(
            strategy=ContextStrategy.RESET_WITH_SUMMARY,
            summary_prompt=(
                "Summarize the buyer's property requirements, any preferences already discussed, "
                "and the current state of the search so the next stage can continue naturally."
            ),
        ),"respond_immediately": True,
    }


def property_discussion_node() -> NodeConfig:
    return {
        "name": "property_discussion",
        "role_message": ROLE_MESSAGE,
        "task_messages": [
            {
                "role": "system",
                "content": PROPERTY_DISCUSSION_PROMPT,
            }
        ],
        "functions": [
            property_details_schema,
            property_comparison_schema,
            schedule_viewing_schema,
            property_search_schema,
        ],
        "context_strategy": ContextStrategyConfig(
            strategy=ContextStrategy.RESET_WITH_SUMMARY,
            summary_prompt=(
                "Summarize the property search results, standout listings, and buyer intent so the "
                "discussion can continue with the most relevant options and next steps."
            ),
        ),"respond_immediately": True,
    }


def comparison_node() -> NodeConfig:
    return {
        "name": "comparison",
        "role_message": ROLE_MESSAGE,
        "task_messages": [
            {
                "role": "system",
                "content": COMPARISON_PROMPT,
            }
        ],
        "functions": [
            property_comparison_schema,
            property_details_schema,
            schedule_viewing_schema,
        ],
        "context_strategy": ContextStrategyConfig(
            strategy=ContextStrategy.RESET_WITH_SUMMARY,
            summary_prompt=(
                "Summarize the properties compared, the trade-offs discussed, and the buyer's likely "
                "decision preference so the next step can continue coherently."
            ),
        ),"respond_immediately": True,
    }


def viewing_node() -> NodeConfig:
    return {
        "name": "viewing",
        "role_message": ROLE_MESSAGE,
        "task_messages": [
            {
                "role": "system",
                "content": VIEWING_PROMPT,
            }
        ],
        "functions": [
            schedule_viewing_schema,
        ],
        "context_strategy": ContextStrategyConfig(
    strategy=ContextStrategy.RESET
),"respond_immediately": True,
    }


def closing_node() -> NodeConfig:
    return {
        "name": "closing",
        "role_message": ROLE_MESSAGE,
        "task_messages": [
            {
                "role": "system",
                "content": CLOSING_PROMPT,
            }
        ],
        "functions": [
            conversation_analysis_schema,
            property_search_schema,
        ],"respond_immediately": True,
    }


def analysis_node() -> NodeConfig:
    return {
        "name": "analysis",
        "role_message": ROLE_MESSAGE,
        "task_messages": [
            {
                "role": "system",
                "content": "Analyze the conversation and save structured CRM reports.",
            }
        ],
        "functions": [
            conversation_analysis_schema,
        ],
        "respond_immediately": True     }


def finalize_node() -> NodeConfig:
    return {
        "name": "finalize",
        "role_message": ROLE_MESSAGE,
        "task_messages": [
            {
                "role": "system",
                "content": FINALIZE_PROMPT,
            }
        ],
        "functions": [
            finalize_conversation_schema,
        ],
        "respond_immediately": True
    }


def build_buyer_flow() -> dict[str, NodeConfig]:
    return {
        "greeting": greeting_node(),
        "requirements": requirements_node(),
        "property_discussion": property_discussion_node(),
        "comparison": comparison_node(),
        "viewing": viewing_node(),
        "closing": closing_node(),
        "analysis": analysis_node(),
        "finalize": finalize_node(),
    }