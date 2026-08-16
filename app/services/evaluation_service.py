"""
app/services/evaluation_service.py

Service for evaluating conversation quality and recommendation accuracy.
Runs asynchronously after a call ends to analyze:
- Requirement understanding
- Property relevance
- Conversation quality
- Tool/search usage
- Recommendation quality
- Call completion
"""

from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from loguru import logger
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.conversation import ConversationSession, ConversationMessage
from app.db.models.property import Property
from app.db.models.viewing import Viewing
from app.db.crud.evaluation import evaluation_repo


class ConversationEvaluator:
    """Evaluates conversation quality based on finalized transcript and interactions."""

    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def evaluate_conversation(self, session_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Analyze a completed conversation and generate evaluation scores.
        
        Returns a dict with:
        - overall_score
        - category_scores
        - strengths
        - issues
        - evaluation_details
        """

        try:
            session = self.db.query(ConversationSession).filter(
                ConversationSession.id == session_id
            ).first()

            if not session:
                logger.warning(f"[Evaluator] Session {session_id} not found")
                return None

            # Extract evaluation data
            messages = self.db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session_id
            ).order_by(ConversationMessage.created_at).all()

            # Extract structured data from analysis field
            analysis = session.analysis or {}

            # Score each dimension
            scores = self._calculate_scores(
                messages=messages,
                analysis=analysis,
                session=session,
            )

            strengths, issues = self._generate_feedback(
                messages=messages,
                analysis=analysis,
                scores=scores,
                session=session,
            )

            # Store evaluation in database
            evaluation = evaluation_repo.create_evaluation(
                db=self.db,
                session_id=session_id,
                overall_score=scores.get("overall"),
                requirement_understanding=scores.get("requirement_understanding"),
                property_relevance=scores.get("property_relevance"),
                conversation_quality=scores.get("conversation_quality"),
                search_tool_usage=scores.get("search_tool_usage"),
                recommendation_quality=scores.get("recommendation_quality"),
                transcript_quality=scores.get("transcript_quality"),
                call_completion=scores.get("call_completion"),
                strengths=strengths,
                issues=issues,
                evaluation_details={
                    "message_count": len(messages),
                    "call_duration_seconds": self._calculate_duration(session),
                    "user_messages": len([m for m in messages if m.speaker == "user"]),
                    "assistant_messages": len([m for m in messages if m.speaker == "assistant"]),
                    "analysis": analysis,
                },
            )

            logger.info(f"[Evaluator] Evaluation completed for session {session_id}: score={scores.get('overall')}")
            
            return {
                "session_id": session_id,
                "overall_score": scores.get("overall"),
                "scores": scores,
                "strengths": strengths,
                "issues": issues,
                "evaluation_id": evaluation.id,
            }

        except Exception as e:
            logger.error(f"[Evaluator] Error evaluating session {session_id}: {e}")
            return None

    def _calculate_scores(
        self,
        messages: List[ConversationMessage],
        analysis: Dict[str, Any],
        session: ConversationSession,
    ) -> Dict[str, int]:
        """Calculate category scores based on conversation data."""

        scores = {
            "requirement_understanding": self._score_requirement_understanding(analysis),
            "property_relevance": self._score_property_relevance(analysis),
            "conversation_quality": self._score_conversation_quality(messages, analysis),
            "search_tool_usage": self._score_search_tool_usage(analysis),
            "recommendation_quality": self._score_recommendation_quality(analysis),
            "transcript_quality": self._score_transcript_quality(messages),
            "call_completion": self._score_call_completion(session, analysis),
        }

        weights = {
            "requirement_understanding": 0.15,
            "property_relevance": 0.20,
            "conversation_quality": 0.15,
            "search_tool_usage": 0.15,
            "recommendation_quality": 0.20,
            "transcript_quality": 0.10,
            "call_completion": 0.05,
        }

        overall = sum(scores[k] * weights[k] for k in scores.keys())
        scores["overall"] = int(round(overall))

        return scores

    def _score_requirement_understanding(self, analysis: Dict[str, Any]) -> int:
        """Score Nova's understanding of user's stated requirements."""
        
        extracted_requirements = analysis.get("extracted_requirements", {})
        if not extracted_requirements:
            return 50  # Neutral if no data

        # Check for key dimensions
        required_fields = ["location"]  # Minimum required
        optional_fields = ["budget", "bedrooms", "bathrooms", "property_type"]

        found_required = sum(
            1 for field in required_fields 
            if extracted_requirements.get(field)
        )
        found_optional = sum(
            1 for field in optional_fields 
            if extracted_requirements.get(field)
        )

        # Score: found_required + partial credit for optional
        score = 70 + (found_required * 10) + (found_optional * 5)
        return min(100, score)

    def _score_property_relevance(self, analysis: Dict[str, Any]) -> int:
        """Score how relevant recommended properties were to requirements."""
        
        recommended = analysis.get("properties_recommended", [])
        requirements = analysis.get("extracted_requirements", {})

        if not recommended or not requirements:
            return 50

        # Count properties that match key requirements
        matches = 0
        for prop in recommended:
            if self._property_matches_requirements(prop, requirements):
                matches += 1

        # Score based on match percentage
        match_percentage = (matches / len(recommended)) * 100 if recommended else 0
        return int(match_percentage)

    def _score_conversation_quality(
        self,
        messages: List[ConversationMessage],
        analysis: Dict[str, Any],
    ) -> int:
        """Score naturalness and effectiveness of conversation."""
        
        if not messages:
            return 50

        # Factors:
        # - Conversation length (too short = bad, too long = inefficient)
        # - Message count balance
        # - Repetition detection
        # - Question relevance

        msg_count = len(messages)
        user_msgs = len([m for m in messages if m.speaker == "user"])
        assistant_msgs = len([m for m in messages if m.speaker == "assistant"])

        # Ideal is roughly balanced
        balance_score = min(100, 100 - abs(user_msgs - assistant_msgs) * 10)

        # Length score: good if between 10-30 messages total
        if msg_count < 8:
            length_score = 60
        elif msg_count > 50:
            length_score = 70
        else:
            length_score = 90

        # Repetition: check if same question asked multiple times
        repetition_penalty = analysis.get("repetition_penalty", 0)

        score = (balance_score * 0.4) + (length_score * 0.6) - repetition_penalty
        return max(0, min(100, int(score)))

    def _score_search_tool_usage(self, analysis: Dict[str, Any]) -> int:
        """Score effectiveness of search and tool usage."""
        
        search_count = len(analysis.get("searches_performed", []))
        tool_calls = analysis.get("tool_calls_made", 0)

        # Good: 1-3 searches, 3-5 total tool calls
        if 1 <= search_count <= 3 and 3 <= tool_calls <= 5:
            return 90
        elif search_count == 0:
            return 40  # No search = bad
        elif search_count > 5:
            return 70  # Too many searches
        else:
            return 75

    def _score_recommendation_quality(self, analysis: Dict[str, Any]) -> int:
        """Score quality of Nova's final recommendations."""
        
        recommended = analysis.get("properties_recommended", [])
        
        if not recommended:
            return 50

        # Properties recommended without explanation = lower score
        has_reasoning = analysis.get("recommendation_reasoning", "")
        
        # Score based on number of recommendations (3-5 is ideal)
        if 3 <= len(recommended) <= 5:
            base_score = 85
        elif 1 <= len(recommended) <= 7:
            base_score = 75
        else:
            base_score = 60

        # Bonus if reasoning provided
        if has_reasoning:
            base_score = min(100, base_score + 10)

        return base_score

    def _score_transcript_quality(self, messages: List[ConversationMessage]) -> int:
        """Score quality of transcribed messages (finalization, completeness)."""
        
        if not messages:
            return 50

        # Check for message quality
        empty_or_short = sum(1 for m in messages if len(m.message.strip()) < 3)
        avg_length = sum(len(m.message) for m in messages) / len(messages) if messages else 0

        if empty_or_short > len(messages) * 0.1:  # >10% too short
            return 60

        if avg_length < 10:
            return 70

        return 90

    def _score_call_completion(
        self,
        session: ConversationSession,
        analysis: Dict[str, Any],
    ) -> int:
        """Score whether call completed successfully."""
        
        # Completed = user got what they needed
        if session.completed and session.status == "COMPLETED":
            return 95

        # Has properties + analysis
        if analysis.get("properties_recommended"):
            return 85

        # Has analysis but no properties
        if analysis.get("summary"):
            return 70

        # Inconclusive
        return 50

    def _generate_feedback(
        self,
        messages: List[ConversationMessage],
        analysis: Dict[str, Any],
        scores: Dict[str, int],
        session: ConversationSession,
    ) -> tuple[List[str], List[str]]:
        """Generate human-readable strengths and issues."""

        strengths = []
        issues = []

        # Requirement understanding
        if scores.get("requirement_understanding", 0) >= 80:
            extracted = analysis.get("extracted_requirements", {})
            if "location" in extracted:
                strengths.append(f"Correctly identified {extracted['location']} as preferred location.")
            if "budget" in extracted:
                strengths.append(f"Correctly respected £{extracted['budget']} budget constraint.")
            if "bedrooms" in extracted:
                strengths.append(f"Correctly matched {extracted['bedrooms']} bedroom requirement.")
        elif scores.get("requirement_understanding", 0) < 60:
            issues.append("Failed to extract key user requirements from conversation.")

        # Property relevance
        if scores.get("property_relevance", 0) >= 80:
            strengths.append("Recommended properties closely matched user's stated requirements.")
        elif scores.get("property_relevance", 0) < 60:
            issues.append("Some recommended properties did not match user requirements.")

        # Conversation quality
        if scores.get("conversation_quality", 0) >= 80:
            strengths.append("Conversation flowed naturally without unnecessary repetition.")
        elif scores.get("conversation_quality", 0) < 60:
            issues.append("Conversation had inefficient flow or repeated questions.")

        # Search tool usage
        if scores.get("search_tool_usage", 0) >= 80:
            strengths.append("Appropriate number and timing of property searches.")
        elif scores.get("search_tool_usage", 0) < 50:
            issues.append("Search strategy could be improved - too few or too many searches.")

        # Recommendation quality
        if scores.get("recommendation_quality", 0) >= 85:
            strengths.append("Recommendations were well-reasoned and relevant.")
        elif scores.get("recommendation_quality", 0) < 70:
            issues.append("Recommendations lacked clear reasoning or relevance.")

        # Call completion
        if session.completed:
            strengths.append("Call completed successfully with results provided to user.")
        else:
            issues.append("Call did not complete normally - user may not have received full assistance.")

        return strengths or ["Call took place and basic data was collected."], issues or []

    def _property_matches_requirements(
        self,
        property_data: Dict[str, Any],
        requirements: Dict[str, Any],
    ) -> bool:
        """Check if a property matches the user's stated requirements."""
        
        # Location match
        if "location" in requirements:
            prop_city = property_data.get("city", "").lower()
            req_location = str(requirements.get("location", "")).lower()
            if prop_city != req_location:
                return False

        # Budget match (property price <= max budget)
        if "budget" in requirements:
            try:
                max_budget = float(requirements.get("budget", 0))
                prop_price = float(property_data.get("price", 0))
                if prop_price > max_budget:
                    return False
            except (ValueError, TypeError):
                pass

        # Bedroom match
        if "bedrooms" in requirements:
            try:
                req_beds = int(requirements.get("bedrooms", 0))
                prop_beds = int(property_data.get("bedrooms", 0))
                if prop_beds < req_beds:
                    return False
            except (ValueError, TypeError):
                pass

        return True

    def _calculate_duration(self, session: ConversationSession) -> int:
        """Calculate call duration in seconds."""
        
        if not session.ended_at or not session.started_at:
            return 0

        duration = session.ended_at - session.started_at
        return int(duration.total_seconds())


# Singleton instance
evaluator = ConversationEvaluator()
