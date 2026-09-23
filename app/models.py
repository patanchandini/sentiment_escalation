from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel

class Sentiment(str, Enum):
    POSITIVE   = "positive"
    NEUTRAL    = "neutral"
    NEGATIVE   = "negative"
    FRUSTRATED = "frustrated"
    URGENT     = "urgent"
    SARCASTIC  = "sarcastic"

class Risk(str, Enum):
    ACCOUNT_COMPROMISE = "account_compromise"
    DUPLICATE_PAYMENT  = "duplicate_payment"
    LEGAL_THREAT       = "legal_threat"

class Queue(str, Enum):
    STANDARD          = "standard"
    ON_CALL           = "on_call"
    NEXT_BUSINESS_DAY = "next_business_day"
    HUMAN_ESCALATION  = "human_escalation"

# ---- API schemas ----
class MessageIn(BaseModel):
    text: str
    timestamp: Optional[datetime] = None   # injectable for tests

class HistoryMessage(BaseModel):
    text: str
    timestamp: datetime

class AnalyzeRequest(BaseModel):
    message: MessageIn
    history: List[HistoryMessage] = []

class AnalyzeResponse(BaseModel):
    language: str
    sentiment: str
    confidence: float
    scores: Dict[str, float]
    risks: List[str]
    queue: str
    escalate: bool
    tone: str
    scheduled_for: Optional[str] = None
    escalation: Optional[Dict] = None

# ---- Internal dataclasses ----
@dataclass
class SentimentResult:
    label: Sentiment
    confidence: float
    scores: Dict[str, float]

@dataclass
class Escalation:
    reason: str
    activated_condition: str
    summary: str
    timestamp: datetime = field(default_factory=datetime.utcnow)