from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


class CallUsageTracker:
    """Tracks provider usage for a single call and exposes a JSON-safe summary."""

    def __init__(self, session_id: str | None = None):
        self.session_id = session_id
        self._llm_usage: List[dict[str, Any]] = []
        self._tts_usage: List[dict[str, Any]] = []
        self._stt_usage: List[dict[str, Any]] = []

    def record_llm_usage(
        self,
        *,
        provider: str,
        model: str | None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        cache_read_tokens: int | None = None,
        reasoning_tokens: int | None = None,
        usage_source: str = "actual",
    ) -> None:
        entry = {
            "provider": provider,
            "model": model,
            "prompt_tokens": int(prompt_tokens or 0),
            "completion_tokens": int(completion_tokens or 0),
            "total_tokens": int(total_tokens or (prompt_tokens or 0) + (completion_tokens or 0)),
            "cache_read_tokens": int(cache_read_tokens) if cache_read_tokens is not None else None,
            "reasoning_tokens": int(reasoning_tokens) if reasoning_tokens is not None else None,
            "usage_source": usage_source,
        }
        self._llm_usage.append(entry)

    def record_tts_usage(
        self,
        *,
        provider: str,
        model: str | None,
        characters: int = 0,
        usage_source: str = "actual",
    ) -> None:
        self._tts_usage.append(
            {
                "provider": provider,
                "model": model,
                "characters": int(characters or 0),
                "usage_source": usage_source,
            }
        )

    def record_stt_usage(
        self,
        *,
        provider: str,
        model: str | None,
        audio_seconds: float | None = None,
        usage_source: str = "actual",
    ) -> None:
        self._stt_usage.append(
            {
                "provider": provider,
                "model": model,
                "audio_seconds": float(audio_seconds) if audio_seconds is not None else None,
                "usage_source": usage_source,
            }
        )

    def snapshot_summary(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "llm": self._summarize_usage(self._llm_usage),
            "tts": self._summarize_usage(self._tts_usage),
            "stt": self._summarize_usage(self._stt_usage),
            "totals": {
                "llm_prompt_tokens": sum(item.get("prompt_tokens", 0) for item in self._llm_usage),
                "llm_completion_tokens": sum(item.get("completion_tokens", 0) for item in self._llm_usage),
                "llm_total_tokens": sum(item.get("total_tokens", 0) for item in self._llm_usage),
                "tts_characters": sum(item.get("characters", 0) for item in self._tts_usage),
                "stt_audio_seconds": sum(
                    item.get("audio_seconds") or 0 for item in self._stt_usage
                ),
            },
        }

    @staticmethod
    def _summarize_usage(entries: List[dict[str, Any]]) -> List[dict[str, Any]]:
        grouped: Dict[str, Dict[str, Any]] = {}
        for entry in entries:
            key = (entry.get("provider") or "unknown", entry.get("model") or "unknown")
            bucket = grouped.setdefault(
                key,
                {
                    "provider": entry.get("provider") or "unknown",
                    "model": entry.get("model") or "unknown",
                    "usage_source": entry.get("usage_source") or "actual",
                    "count": 0,
                },
            )
            bucket["count"] += 1
            for metric_name in ("prompt_tokens", "completion_tokens", "total_tokens", "characters", "audio_seconds"):
                if metric_name in entry:
                    bucket[metric_name] = (bucket.get(metric_name) or 0) + (entry.get(metric_name) or 0)
            if entry.get("cache_read_tokens") is not None:
                bucket["cache_read_tokens"] = (bucket.get("cache_read_tokens") or 0) + int(entry.get("cache_read_tokens") or 0)
            if entry.get("reasoning_tokens") is not None:
                bucket["reasoning_tokens"] = (bucket.get("reasoning_tokens") or 0) + int(entry.get("reasoning_tokens") or 0)

        return [
            {
                **metrics,
                "input_tokens": metrics.get("prompt_tokens", 0),
                "output_tokens": metrics.get("completion_tokens", 0),
            }
            for metrics in grouped.values()
        ]
