import re
from typing import List
from app.models import Risk

RISK_PATTERNS = {
    Risk.ACCOUNT_COMPROMISE: [
        r"\b(hack(ed)?|compromis(ed)?|unauthori[sz]ed|stolen|breach)\b",
        r"\b(cuenta.*(robad|hackead)|compte.*pirat|konto.*gehackt)\b",
        r"(账户.*(被盗|入侵)|アカウント.*(乗っ取|不正))",
    ],
    Risk.DUPLICATE_PAYMENT: [
        r"\b(charged twice|double[- ]charged|duplicate (payment|charge)|billed twice)\b",
        r"\b(cobr(o|ado) dos veces|double paiement|doppelt (abgebucht|berechnet))\b",
        r"(重复(扣款|付款)|二重請求)",
    ],
    Risk.LEGAL_THREAT: [
        r"\b(lawyer|attorney|sue|legal action|litigation|gdpr|ftc|consumer court)\b",
        r"\b(abogado|demandar|avocat|poursuivre|anwalt|klagen)\b",
        r"(律师|起诉|诉讼|法律)",
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