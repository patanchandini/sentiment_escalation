from app.models import Escalation
from typing import List

class EscalationLog:
    def __init__(self):
        self.entries: List[Escalation] = []

    def record(self, reason: str, condition: str,
               history, current_text: str) -> Escalation:
        summary = self._summarize(history, current_text)
        entry = Escalation(reason=reason,
                           activated_condition=condition,
                           summary=summary)
        self.entries.append(entry)
        return entry

    @staticmethod
    def _summarize(history, current_text: str) -> str:
        parts = [m.text[:80] for m in history[-4:]] + [current_text[:80]]
        return " | ".join(parts)