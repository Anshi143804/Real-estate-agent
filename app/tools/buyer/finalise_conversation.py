from datetime import datetime
import asyncio

from sqlalchemy.orm import Session
from loguru import logger

from app.db.crud.buyer import buyer_repo
from app.db.crud.conversation import conversation_repo
from app.schemas.buyer.conversation_report import ConversationReport
from app.services.evaluation_service import ConversationEvaluator


def _get_or_create_buyer_lead(db: Session, session, report: ConversationReport):
    """
    Resolve the BuyerLead this conversation belongs to.

    Priority:
    1. session.buyer_lead_id, if a lead was already linked earlier in the
       call (e.g. schedule_viewing() created/found one via phone number).
    2. An existing lead matching the phone number captured in the report.
    3. An existing lead matching the email captured in the report.
    4. Otherwise create a new lead from the contact info in the report.
    """

    if session.buyer_lead_id:
        existing = buyer_repo.get_buyer(db, str(session.buyer_lead_id))
        if existing:
            return existing

    phone = report.contact.phone_number
    email = report.contact.email

    if phone:
        existing = buyer_repo.get_by_phone(db=db, phone=phone)
        if existing:
            return existing

    if email:
        existing = buyer_repo.get_by_email(db=db, email=email)
        if existing:
            return existing

    return buyer_repo.create_buyer(
        db=db,
        name=report.contact.full_name or "Anonymous Buyer",
        phone=phone,
        email=email,
        status="New",
    )


def finalize_conversation(
    db: Session,
    session_id: str,
    report: ConversationReport,
):
    """
    Finalizes a buyer conversation.

    Responsibilities:
    - Save the AI-generated call summary/analysis onto conversation_sessions
    - Resolve (or create) the buyer_leads row this call belongs to, and
      save the same summary onto it (summary_text / summary_json), plus
      any requirement fields the call surfaced
    - Link conversation_sessions.buyer_lead_id -> buyer_leads.id
    - Mark the session completed
    - Return a result summary
    """

    session = conversation_repo.get_session(
        db=db,
        session_id=session_id,
    )

    if session is None:
        raise ValueError(f"Conversation '{session_id}' not found.")

    if isinstance(report, dict):
        report = ConversationReport.model_validate(report)

    report_json = report.model_dump(mode="json")

    session = conversation_repo.update_summary(
        db=db,
        session=session,
        summary=report.insights.summary,
    )

    session.analysis = report_json

    # NOTE: the table has `ended_at` (timestamp) and `completed` (bool) -
    # there is no `completed_at` column, so setting it was a silent no-op.
    session.ended_at = datetime.utcnow()
    session.completed = True
    session.status = "COMPLETED"

    # -------------------------
    # buyer_leads
    # -------------------------

    buyer = _get_or_create_buyer_lead(db, session, report)

    buyer.summary_text = report.insights.summary
    buyer.summary_json = report_json

    # Only overwrite requirement fields the AI actually captured this call -
    # don't clobber existing data with nulls just because this particular
    # call didn't mention them again.
    prefs = report.preferences
    contact = report.contact

    if contact.full_name:
        buyer.name = contact.full_name
    if contact.email:
        buyer.email = contact.email
    if contact.phone_number:
        buyer.phone = contact.phone_number

    if prefs.min_budget is not None:
        buyer.budget_min = prefs.min_budget
    if prefs.max_budget is not None:
        buyer.budget_max = prefs.max_budget
    if prefs.property_type:
        buyer.property_type = prefs.property_type
    if prefs.bedrooms is not None:
        buyer.bedrooms = prefs.bedrooms
    if prefs.bathrooms is not None:
        buyer.bathrooms = prefs.bathrooms
    if prefs.first_time_buyer is not None:
        buyer.first_time_buyer = prefs.first_time_buyer
    if prefs.move_in_timeline:
        buyer.moving_timeline = prefs.move_in_timeline
    if prefs.city or prefs.locality:
        buyer.preferred_locations = [
            loc for loc in [prefs.city, prefs.locality] if loc
        ]

    buyer.status = "Qualified" if report.qualification.qualified else "Contacted"

    # -------------------------
    # Link session -> lead
    # -------------------------

    session.buyer_lead_id = buyer.id

    db.commit()
    db.refresh(session)
    db.refresh(buyer)

    # Trigger evaluation asynchronously (doesn't block the response)
    try:
        evaluator = ConversationEvaluator()
        evaluator.evaluate_conversation(session.id)
        evaluator.close()
        logger.info(f"[Finalize] Evaluation triggered for session {session.id}")
    except Exception as e:
        logger.warning(f"[Finalize] Evaluation failed for session {session.id}: {e}")

    return {
        "success": True,
        "message": "Conversation finalized successfully.",
        "session_id": session.id,
        "buyer_lead_id": buyer.id,
        "lead_score": report.qualification.lead_score,
        "priority": report.qualification.priority,
        "qualified": report.qualification.qualified,
    }