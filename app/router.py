from datetime import datetime
from typing import List, Optional
from app.models import (Sentiment, Risk, Queue, SentimentResult,
                        HistoryMessage, Escalation)
from app import config
from app.time_utils import is_business_hours, next_business_day, minutes_since
from app.logger import EscalationLog

class Router:
    def __init__(self, log: Optional[EscalationLog] = None):
        self.log = log or EscalationLog()

    # ---------- public entry ----------
    def route(self, text: str, sentiment: SentimentResult,
              risks: List[Risk], history: List[HistoryMessage],
              now: datetime, conversation_opened_at: Optional[datetime] = None):
        decision = {
            "queue": Queue.STANDARD,
            "escalate": False,
            "tone": "professional",
            "scheduled_for": None,
            "escalation": None,
        }

        # 1) HIGH-RISK  → always escalate
        if risks:
            esc = self.log.record(
                reason=f"High-risk issue: {[r.value for r in risks]}",
                condition="high_risk_pattern",
                history=history, current_text=text)
            decision.update(queue=Queue.HUMAN_ESCALATION,
                            escalate=True,
                            escalation=esc.__dict__)
            return decision

        # 2) REPEATED NEGATIVES
        if self._recent_negatives(history) >= config.REPEATED_NEGATIVE_THRESHOLD:
            esc = self.log.record(
                reason="Repeated negative messages",
                condition=f"repeated_negative>={config.REPEATED_NEGATIVE_THRESHOLD}",
                history=history, current_text=text)
            decision.update(queue=Queue.HUMAN_ESCALATION,
                            escalate=True,
                            escalation=esc.__dict__)
            return decision

        # 3) 15-MIN UNRESOLVED NEGATIVE
        if (conversation_opened_at
                and sentiment.label in (Sentiment.NEGATIVE, Sentiment.FRUSTRATED)
                and minutes_since(conversation_opened_at, now)
                    > config.UNRESOLVED_NEGATIVE_MINUTES):
            esc = self.log.record(
                reason="Negative conversation unresolved > 15 min",
                condition="unresolved_negative_15min",
                history=history, current_text=text)
            decision.update(queue=Queue.HUMAN_ESCALATION,
                            escalate=True,
                            escalation=esc.__dict__)
            return decision

        # 4) AFTER-HOURS URGENT
        if sentiment.label == Sentiment.URGENT and not is_business_hours(now):
            decision.update(queue=Queue.ON_CALL, tone="empathetic_urgent")
            return decision

        # 5) AFTER-HOURS NORMAL NEGATIVE
        if sentiment.label in (Sentiment.NEGATIVE, Sentiment.FRUSTRATED) \
                and not is_business_hours(now):
            decision.update(
                queue=Queue.NEXT_BUSINESS_DAY,
                tone="apologetic",
                scheduled_for=next_business_day(now).isoformat())
            return decision

        # 6) STANDARD — tone only
        decision["tone"] = self._tone_for(sentiment.label)
        return decision

    # ---------- helpers ----------
    @staticmethod
    def _recent_negatives(history: List[HistoryMessage]) -> int:
        window = history[-config.REPEATED_NEGATIVE_WINDOW:]
        import re
        neg = re.compile(r"\b(bad|broken|terrible|worst|again|still|"
                         r"no one|useless)\b", re.IGNORECASE)
        return sum(1 for m in window if neg.search(m.text))

    @staticmethod
    def _tone_for(label: Sentiment) -> str:
        return {
            Sentiment.POSITIVE:   "warm",
            Sentiment.NEUTRAL:    "professional",
            Sentiment.NEGATIVE:   "apologetic",
            Sentiment.FRUSTRATED: "empathetic",
            Sentiment.URGENT:     "empathetic_urgent",
            Sentiment.SARCASTIC:  "calm_professional",
        }[label]