import re
from typing import List
from app.models import Risk

RISK_PATTERNS = {
    Risk.ACCOUNT_COMPROMISE: [
        r"\b(hack(ed|ing)?|compromis(ed|ing)?|unauthori[sz]ed|"
        r"stolen|breach(ed)?|someone logged in)\b",
    ],
    Risk.DUPLICATE_PAYMENT: [
        r"\b(charged twice|double[- ]charged|duplicate (payment|charge)|"
        r"billed twice|two (payments|charges)|overcharged)\b",
    ],
    Risk.LEGAL_THREAT: [
        r"\b(lawyer|attorney|sue|suing|legal action|litigation|"
        r"gdpr|ftc|consumer court|take you to court)\b",
    ],
}

def detect_risks(text: str) -> List[Risk]:
    found = []
    for risk, patterns in RISK_PATTERNS.items():
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                found.append(risk)
                break
    return found