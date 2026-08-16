from typing import Any
import asyncio
from datetime import datetime
from loguru import logger

# DB Session Factory
from app.db.database import SessionLocal

# Pydantic Schemas used by database tools
from app.schemas.buyer.property_search import PropertySearchRequest
from app.schemas.buyer.property_details import PropertyDetailsRequest
from app.schemas.buyer.property_comparison import PropertyComparisonRequest
from app.schemas.buyer.viewing import ScheduleViewingRequest

# Business & Database Tool Functions
from app.db.crud.conversation import conversation_repo
from app.services.call_analysis import ConversationAnalyzer
from app.tools.buyer.property_search import find_matching_properties
from app.tools.buyer.property_details import get_property_details
from app.tools.buyer.property_comparison import compare_properties
from app.tools.buyer.schedule_viewing import schedule_viewing
from app.tools.buyer.finalise_conversation import finalize_conversation


async def proceed_to_requirements_handler(
    args: dict[str, Any] = None,
    flow_manager: Any = None,
):
    """
    Called after Nova introduces herself to transition the conversation
    from the 'greeting' node to the 'requirements' node.
    """
    logger.info("⚡ [TRANSITION]: Moving flow from 'greeting' -> 'requirements'")
    
    from app.flows.buyer_flow import requirements_node

    return {"status": "moved_to_requirements"}, requirements_node()



async def property_search_handler(
    args: dict[str, Any],
    flow_manager: Any = None,
):
    """
    Executes property search in the database based on criteria passed from LLM.
    Normalizes all text input values to lowercase to prevent database string mismatches.
    """
    logger.info(f"🔥 [TOOL CALL]: property_search_handler raw args: {args}")

    search_args = {}

    def clean_str(key: str) -> str | None:
        val = args.get(key)
        return str(val).strip().lower() if val is not None else None

    city = clean_str("city")
    if city:
        search_args["city"] = city

    locality = clean_str("locality")
    if locality:
        search_args["locality"] = locality

    property_type = clean_str("property_type")
    if property_type:
        search_args["property_type"] = property_type

    listing_type = clean_str("listing_type")
    if listing_type:
        search_args["listing_type"] = listing_type

    if "bedrooms" in args:
        search_args["min_bedrooms"] = args["bedrooms"]
    elif "min_bedrooms" in args:
        search_args["min_bedrooms"] = args["min_bedrooms"]

    if "bathrooms" in args:
        search_args["min_bathrooms"] = args["bathrooms"]
    elif "min_bathrooms" in args:
        search_args["min_bathrooms"] = args["min_bathrooms"]

    if "budget_max" in args:
        search_args["max_budget"] = args["budget_max"]
    elif "max_price" in args:
        search_args["max_budget"] = args["max_price"]
    elif "max_budget" in args:
        search_args["max_budget"] = args["max_budget"]

    if "budget_min" in args:
        search_args["min_budget"] = args["budget_min"]
    elif "min_price" in args:
        search_args["min_budget"] = args["min_price"]
    elif "min_budget" in args:
        search_args["min_budget"] = args["min_budget"]
        

    if "reception_rooms" in args:
        search_args["min_reception_rooms"] = (
            args["reception_rooms"]
        )
    
    elif "min_reception_rooms" in args:
        search_args["min_reception_rooms"] = (
            args["min_reception_rooms"]
        )
    
    
    if "min_area_sqft" in args:
        search_args["min_area_sqft"] = (
            args["min_area_sqft"]
        )
    
    if "max_area_sqft" in args:
        search_args["max_area_sqft"] = (
            args["max_area_sqft"]
        )
    
    
    if "furnished" in args:
        search_args["furnished"] = (
            clean_str("furnished")
        )
    
    
    if "parking" in args:
        search_args["parking"] = (
            args["parking"]
        )
    
    
    if "garden" in args:
        search_args["garden"] = (
            args["garden"]
        )
    
    
    if "garage" in args:
        search_args["garage"] = (
            args["garage"]
        )
    
    
    if "balcony" in args:
        search_args["balcony"] = (
            args["balcony"]
        )
    
    
    if "terrace" in args:
        search_args["terrace"] = (
            args["terrace"]
        )
    
    
    if "pets_allowed" in args:
        search_args["pets_allowed"] = (
            args["pets_allowed"]
        )
    
    
    if "tenure" in args:
        search_args["tenure"] = (
            clean_str("tenure")
        )
    
        if "features" in args and isinstance(args["features"], list):
            search_args["features"] = [str(f).strip().lower() for f in args["features"]]

    logger.info(f"✨ Normalized search criteria: {search_args}")

    db = SessionLocal()
    try:
        search_request = PropertySearchRequest(**search_args)
        result = find_matching_properties(
            db=db,
            request=search_request,
        )
        serialized_result = result.model_dump(mode="json")
    except Exception as e:
        logger.error(f"❌ Error in property_search_handler: {e}")
        serialized_result = {"status": "error", "message": str(e)}
    finally:
        db.close()

    from app.flows.buyer_flow import property_discussion_node

    return serialized_result, property_discussion_node()

# ==========================================================
# Property Details
# ==========================================================

async def property_details_handler(
    args: dict[str, Any],
    flow_manager: Any = None,
):
    logger.info(f"🔥 [TOOL CALL]: property_details_handler with args: {args}")

    db = SessionLocal()
    try:
        details_request = PropertyDetailsRequest(**args)
        result = get_property_details(
            db=db,
            request=details_request,
        )
        serialized_result = result.model_dump(mode="json")
    except Exception as e:
        logger.error(f"❌ Error in property_details_handler: {e}")
        serialized_result = {"status": "error", "message": str(e)}
    finally:
        db.close()

    return serialized_result, None


# ==========================================================
# Property Comparison
# ==========================================================

async def property_comparison_handler(
    args: dict[str, Any],
    flow_manager: Any = None,
):
    logger.info(f"🔥 [TOOL CALL]: property_comparison_handler with args: {args}")

    db = SessionLocal()
    try:
        comparison_request = PropertyComparisonRequest(**args)
        result = compare_properties(
            db=db,
            request=comparison_request,
        )
        serialized_result = result.model_dump(mode="json")
    except Exception as e:
        logger.error(f"❌ Error in property_comparison_handler: {e}")
        serialized_result = {"status": "error", "message": str(e)}
    finally:
        db.close()

    from app.flows.buyer_flow import comparison_node

    return serialized_result, comparison_node()


# ==========================================================
# Schedule Viewing
# ==========================================================

async def schedule_viewing_handler(
    args: dict[str, Any],
    flow_manager: Any = None,
):
    logger.info(f"🔥 [TOOL CALL]: schedule_viewing_handler with args: {args}")

    db = SessionLocal()
    try:
        viewing_request = ScheduleViewingRequest(**args)
        result = schedule_viewing(
            db=db,
            request=viewing_request,
        )
        serialized_result = result.model_dump(mode="json")
    except Exception as e:
        logger.error(f"❌ Error in schedule_viewing_handler: {e}")
        serialized_result = {"status": "error", "message": str(e)}
    finally:
        db.close()

    from app.flows.buyer_flow import closing_node

    return serialized_result, closing_node()


# ==========================================================
# Conversation Analysis
# ==========================================================

# app/flows/handlers.py

# app/flows/handlers.py

async def conversation_analysis_handler(
    args: dict[str, Any] = None,
    flow_manager: Any = None,
):
    logger.info("🔥 [TOOL CALL]: conversation_analysis_handler")

    messages = []

    raw_messages = []
    if flow_manager is not None:
        try:
            raw_messages = flow_manager.get_current_context()
        except Exception as e:
            logger.warning(f"⚠️ Could not read context from flow_manager: {e}")

    for msg in raw_messages:
        role = None
        content = None

        if isinstance(msg, dict):
            role = msg.get("role")
            content = msg.get("content")
        else:
            inner = getattr(msg, "message", None)
            if isinstance(inner, dict):
                role = inner.get("role")
                content = inner.get("content")
            else:
                role = getattr(msg, "role", None)
                content = getattr(msg, "content", None)

        if not role or content is None:
            continue

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "text" and part.get("text"):
                        text_parts.append(str(part["text"]))
                elif isinstance(part, str):
                    text_parts.append(part)
            content = " ".join(text_parts)

        content = str(content).strip()
        if content:
            messages.append({"role": str(role), "content": content})

    if not messages and args:
        messages = args.get("messages", [])

    session_id = flow_manager.state.get("session_id") if flow_manager else None
    session_id = session_id or (args.get("session_id") if args else None) or "default_session"

    if messages:
        to_save = []
        for msg in messages:
            role = (msg.get("role") or "").lower()
            content = msg.get("content")
            if not content:
                continue
            speaker = "user" if role == "user" else "assistant" if role in ("assistant", "system") else role
            to_save.append({"speaker": speaker, "message": str(content)})

        db = SessionLocal()
        try:
            saved_count = conversation_repo.save_messages(db, session_id=session_id, messages=to_save)
            logger.info(f"✅ Saved {saved_count} conversation_messages rows for session {session_id}")
        except Exception as e:
            logger.error(f"❌ Error saving conversation_messages: {e}")
        finally:
            db.close()

    try:

        analyzer_messages = [
            m for m in messages if m.get("role") in ("user", "assistant", "system")
        ]

        non_empty = [m for m in analyzer_messages if m.get("content")]
        if not non_empty:
            raise ValueError(
                "No transcript content available to analyze - refusing to "
                "call the analyzer (it would fabricate a placeholder report)."
            )

        report_model = ConversationAnalyzer.analyze(analyzer_messages)

        report_model.session_id = session_id
        report_model.completed_at = datetime.utcnow()

        serialized_report = report_model.model_dump(mode="json")

        db = SessionLocal()
        try:
            finalize_conversation(db=db, session_id=session_id, report=report_model)
            logger.info("✅ Conversation report successfully created and saved to DB!")
        finally:
            db.close()

        result = {"status": "success", "report": serialized_report}

    except Exception as e:
        logger.error(f"❌ Error during conversation analysis: {e}")
        result = {"status": "error", "message": str(e)}

    from app.flows.buyer_flow import finalize_node

    return result, finalize_node()


async def finalize_conversation_handler(
    args: dict[str, Any] = None,
    flow_manager: Any = None,
):
    logger.info("🔥 [TOOL CALL]: finalize_conversation_handler")

    session_id = flow_manager.state.get("session_id") if flow_manager else None
    session_id = session_id or (args.get("session_id") if args else None) or "default_session"
    report = args.get("report") if args else None

    usage_summary = None
    if report:
        db = SessionLocal()
        try:
            finalize_conversation(db=db, session_id=session_id, report=report)
        finally:
            db.close()

    if flow_manager is not None:
        usage_summary = flow_manager.state.get("call_usage")
        if hasattr(usage_summary, "snapshot_summary"):
            usage_summary = usage_summary.snapshot_summary()

    if flow_manager is not None and getattr(flow_manager, "task", None) is not None:
        asyncio.create_task(_end_call_after_delay(flow_manager.task))

    return {"success": True, "message": "Session completed.", "usage_summary": usage_summary}, None


async def _end_call_after_delay(task, delay: float = 5.0):

    from pipecat.frames.frames import EndFrame

    await asyncio.sleep(delay)
    await task.queue_frame(EndFrame())