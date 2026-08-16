"""
app/services/event_bridge.py

Bridges Pipecat pipeline events to the browser over the existing WebRTC
data channel, so the frontend can render a live transcript, tool activity,
property cards, booking confirmations and a call summary.

Implemented as a pipeline *observer* (see pipecat.observers.base_observer).
Observers see every frame that moves through the pipeline, in either
direction, without being wired into the pipeline itself - so this is purely
additive and never touches the existing pipeline / flow / tool logic.

Every handler is wrapped defensively: a problem here must never be able to
break the voice pipeline itself.
"""

import time
import uuid
from typing import Any, Optional

from loguru import logger

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    ErrorFrame,
    FunctionCallInProgressFrame,
    FunctionCallResultFrame,
    InterimTranscriptionFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    MetricsFrame,
    TranscriptionFrame,
    TTSSpeakFrame,
    TTSTextFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.metrics.metrics import LLMUsageMetricsData, TTSUsageMetricsData
from pipecat.observers.base_observer import BaseObserver, FramePushed

from app.services.call_usage import CallUsageTracker

# Friendly labels + agent status keyword for each registered tool/handler.
TOOL_META = {
    "proceed_to_requirements_handler": ("Getting your preferences ready", "thinking"),
    "property_search_handler": ("Searching listings...", "searching"),
    "property_details_handler": ("Fetching property details...", "searching"),
    "property_comparison_handler": ("Comparing properties...", "comparing"),
    "schedule_viewing_handler": ("Scheduling your visit...", "scheduling"),
    "conversation_analysis_handler": ("Generating call summary...", "analyzing"),
    "finalize_conversation_handler": ("Wrapping up the call...", "analyzing"),
}


class EventBridgeObserver(BaseObserver):
    """Watches pipeline frames and forwards structured JSON events to the client."""

    def __init__(
        self,
        connection,
        session_id: str = "default_session",
        usage_tracker: Optional[CallUsageTracker] = None,
    ):
        super().__init__()
        self._connection = connection
        self._session_id = session_id
        self._usage_tracker = usage_tracker or CallUsageTracker(session_id)

        # Streaming assistant message state
        self._current_assistant_id: Optional[str] = None
        self._assistant_buffer: str = ""
        self._last_finalized_assistant_id: Optional[str] = None
        self._last_finalized_assistant_text: str = ""

        # Streaming user (interim) message state
        self._current_user_id: Optional[str] = None

        # Tool calls are de-duplicated by their stable tool_call_id (see
        # _seen_tool_call_events below). We deliberately do NOT use a
        # generic "seen frame object" guard here: Python reuses an
        # object's id() once it's garbage collected, so over a multi-
        # minute call a brand new, unrelated frame can end up with the
        # same id() as an old one already marked "seen" - which silently
        # dropped legitimate transcript/TTS updates. tool_call_id is a
        # real UUID from Pipecat, not a memory address, so it's safe.
        self._seen_tool_call_events: set = set()

    def _send(self, payload: dict):
        try:
            payload.setdefault("ts", time.time())
            self._connection.send_app_message(payload)
        except Exception as e:
            logger.debug(f"[EventBridge] failed to send app message: {e}")

    def send_call_started(self):
        self._send({"type": "call_started", "session_id": self._session_id})

    def send_call_ended(self):
        self._send({"type": "call_ended"})

    async def on_push_frame(self, data: FramePushed):
        frame = data.frame

        try:
            if isinstance(frame, UserStartedSpeakingFrame):
                self._current_user_id = f"user-{uuid.uuid4().hex[:8]}"
                self._send({"type": "user_speaking", "speaking": True})
                self._send({"type": "agent_status", "status": "listening"})

            elif isinstance(frame, UserStoppedSpeakingFrame):
                self._send({"type": "user_speaking", "speaking": False})
                self._send({"type": "agent_status", "status": "thinking"})

            elif isinstance(frame, InterimTranscriptionFrame):
                if frame.text:
                    self._send(
                        {
                            "type": "transcript",
                            "id": self._current_user_id or "user-live",
                            "role": "user",
                            "text": frame.text,
                            "final": False,
                        }
                    )

            elif isinstance(frame, TranscriptionFrame):
                self._send(
                    {
                        "type": "transcript",
                        "id": self._current_user_id or f"user-{uuid.uuid4().hex[:8]}",
                        "role": "user",
                        "text": frame.text,
                        "final": True,
                    }
                )
                self._current_user_id = None
                self._send({"type": "agent_status", "status": "thinking"})

            # ---------------- Assistant text (streamed) ----------------
            elif isinstance(frame, LLMFullResponseStartFrame):
                self._current_assistant_id = f"bot-{uuid.uuid4().hex[:8]}"
                self._assistant_buffer = ""
                self._send({"type": "agent_status", "status": "thinking"})

            elif isinstance(frame, TTSTextFrame):
                # Preserve the raw stream in memory for the authoritative final message
                # but do not emit each chunk to the visible transcript UI. The visible
                # transcript should reflect only finalized assistant turns.
                if not self._current_assistant_id:
                    self._current_assistant_id = f"bot-{uuid.uuid4().hex[:8]}"
                    self._assistant_buffer = ""

                next_text = str(frame.text or "").strip()
                if not next_text:
                    return

                current_text = self._assistant_buffer.strip()
                if not current_text:
                    self._assistant_buffer = next_text
                elif next_text.startswith(current_text):
                    self._assistant_buffer = next_text
                elif current_text.startswith(next_text):
                    self._assistant_buffer = current_text
                else:
                    self._assistant_buffer = f"{current_text} {next_text}".strip()

            elif isinstance(frame, LLMFullResponseEndFrame):
                if self._current_assistant_id and self._assistant_buffer:
                    final_text = self._assistant_buffer.strip()
                    self._send(
                        {
                            "type": "transcript",
                            "id": self._current_assistant_id,
                            "role": "assistant",
                            "text": final_text,
                            "final": True,
                        }
                    )
                    self._last_finalized_assistant_id = self._current_assistant_id
                    self._last_finalized_assistant_text = final_text
                self._current_assistant_id = None
                self._assistant_buffer = ""

            elif isinstance(frame, TTSSpeakFrame):
                # Audio playback is not a separate transcript row. The visible transcript is
                # only generated from the authoritative LLM final response path, so TTS
                # spoke events are intentionally ignored here to avoid duplicate Nova rows.
                return

            elif isinstance(frame, MetricsFrame):
                for metric in getattr(frame, "data", []) or []:
                    if isinstance(metric, LLMUsageMetricsData):
                        usage = metric.value
                        self._usage_tracker.record_llm_usage(
                            provider=(metric.processor or "google").split("_")[0] or "google",
                            model=metric.model or "gemini-2.5-flash",
                            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
                            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
                            total_tokens=getattr(usage, "total_tokens", 0) or 0,
                            cache_read_tokens=getattr(usage, "cache_read_input_tokens", None),
                            reasoning_tokens=getattr(usage, "reasoning_tokens", None),
                            usage_source="actual",
                        )
                    elif isinstance(metric, TTSUsageMetricsData):
                        self._usage_tracker.record_tts_usage(
                            provider=(metric.processor or "cartesia").split("_")[0] or "cartesia",
                            model=metric.model or "cartesia-tts",
                            characters=int(metric.value or 0),
                            usage_source="actual",
                        )

            # ---------------- Bot speaking state ----------------
            elif isinstance(frame, BotStartedSpeakingFrame):
                self._send({"type": "agent_status", "status": "speaking"})

            elif isinstance(frame, BotStoppedSpeakingFrame):
                self._send({"type": "agent_status", "status": "listening"})

            # ---------------- Tool / function calls ----------------
            elif isinstance(frame, FunctionCallInProgressFrame):
                dedup_key = ("in_progress", frame.function_name, getattr(frame, "tool_call_id", None))
                if dedup_key in self._seen_tool_call_events:
                    return
                self._seen_tool_call_events.add(dedup_key)

                label, status = TOOL_META.get(
                    frame.function_name, (f"Running {frame.function_name}...", "thinking")
                )
                self._send({"type": "agent_status", "status": status})
                self._send(
                    {
                        "type": "tool_activity",
                        "tool": frame.function_name,
                        "label": label,
                        "status": "started",
                    }
                )

            elif isinstance(frame, FunctionCallResultFrame):
                dedup_key = ("result", frame.function_name, getattr(frame, "tool_call_id", None))
                if dedup_key in self._seen_tool_call_events:
                    return
                self._seen_tool_call_events.add(dedup_key)

                label, _ = TOOL_META.get(
                    frame.function_name, (f"Running {frame.function_name}...", "thinking")
                )
                result = frame.result
                is_error = isinstance(result, dict) and result.get("status") == "error"

                self._send(
                    {
                        "type": "tool_activity",
                        "tool": frame.function_name,
                        "label": label,
                        "status": "error" if is_error else "completed",
                    }
                )

                if not is_error and isinstance(result, dict):
                    self._forward_tool_result(frame.function_name, result)

                self._send({"type": "agent_status", "status": "thinking"})

            # ---------------- Errors ----------------
            elif isinstance(frame, ErrorFrame):
                self._send({"type": "error", "message": str(frame.error)})

        except Exception as e:
            logger.debug(f"[EventBridge] error handling frame {type(frame).__name__}: {e}")

        # Bound memory for very long calls - only recent history is needed.
        if len(self._seen_tool_call_events) > 200:
            self._seen_tool_call_events = set(list(self._seen_tool_call_events)[-100:])

    # ------------------------------------------------------------------
    # Tool result -> UI event mapping
    # ------------------------------------------------------------------

    def _forward_tool_result(self, function_name: str, result: dict):
        if function_name == "property_search_handler" and "properties" in result:
            self._send(
                {
                    "type": "properties",
                    "source": "search",
                    "total_matches": result.get("total_matches", len(result.get("properties", []))),
                    "properties": result.get("properties", []),
                }
            )

        elif function_name == "property_details_handler" and "property_id" in result:
            image_urls = result.get("image_urls") or []
            prop = {
                **result,
                "location": f"{result.get('address', '')}, {result.get('city', '')}".strip(", ") or result.get("city") or "Location on request",
                "image_url": (image_urls or [None])[0] or result.get("image_url"),
                "image_urls": image_urls,
            }
            self._send({"type": "properties", "source": "details", "properties": [prop]})

        elif function_name == "property_comparison_handler" and "properties" in result:
            # `properties` here are ComparedProperty dicts, which already
            # carry an `image_urls` list straight from the DB - forwarded
            # as-is so the frontend can render a gallery per property.
            self._send(
                {
                    "type": "properties",
                    "source": "comparison",
                    "properties": result.get("properties", []),
                    "summary": result.get("summary"),
                }
            )

        elif function_name == "schedule_viewing_handler" and "viewing_id" in result:
            self._send({"type": "booking", "booking": result})

        elif function_name == "conversation_analysis_handler" and "report" in result:
            self._send({"type": "summary", "report": result.get("report")})

        elif function_name == "finalize_conversation_handler":
            self._send({"type": "call_finalized", "usage_summary": self._usage_tracker.snapshot_summary()})
