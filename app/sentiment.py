import re
from app.models import Sentiment, SentimentResult, HistoryMessage
from app.lexicons import load_lexicon

EMOJI_SARCASM = {"😒", "🙃", "😏", "🙄"}

def _score_lexicon(text: str, lang: str) -> dict:
    lex = load_lexicon(lang)
    t = text.lower()
    scores = {s.value: 0.0 for s in Sentiment}
    for label, terms in lex.items():
        for term in terms:
            if term in t:
                scores[label] += 1.0
    return scores

def _apply_sarcasm_rules(text: str, history: list[HistoryMessage],
                         scores: dict) -> dict:
    t = text.lower()

    # 1. Surface positive + negative history = sarcasm
    hist_neg = sum(
        1 for m in history
        if re.search(r"\b(bad|broken|terrible|again|still|worst)\b",
                     m.text.lower())
    )
    if scores["positive"] > 0 and hist_neg >= 2:
        scores["sarcastic"] += 1.5
        scores["positive"] = max(0.0, scores["positive"] - 1.0)

    # 2. Ellipsis after praise
    if re.search(r"(great|perfect|wonderful|awesome)\s*(\.\.\.|…)", t):
        scores["sarcastic"] += 1.5

    # 3. "Oh great", "Yeah right", "Sure sure"
    if re.search(r"\b(oh|yeah|sure)[, ]+(great|perfect|wonderful|right)\b", t):
        scores["sarcastic"] += 1.5

    # 4. Sarcastic emoji
    if any(e in text for e in EMOJI_SARCASM):
        scores["sarcastic"] += 0.8

    return scores

def _apply_frustration_rules(text: str, scores: dict) -> dict:
    t = text.lower()
    if re.search(r"\b(again|still|yet again|keeps? (happening|failing))\b", t):
        scores["frustrated"] += 1.0
    if text.count("!") >= 2 or re.search(r"[A-Z]{4,}", text):
        scores["frustrated"] += 0.5
    return scores

def _apply_urgency_rules(text: str, scores: dict) -> dict:
    if re.search(r"\b(urgent|asap|right now|immediately)\b", text.lower()):
        scores["urgent"] += 1.0
    return scores

def _normalize(scores: dict) -> dict:
    total = sum(scores.values())
    if total == 0:
        return {k: 0.0 for k in scores}
    return {k: round(v / total, 3) for k, v in scores.items()}

def analyze_sentiment(text: str, lang: str,
                      history: list[HistoryMessage]) -> SentimentResult:
    scores = _score_lexicon(text, lang)
    scores = _apply_sarcasm_rules(text, history, scores)
    scores = _apply_frustration_rules(text, scores)
    scores = _apply_urgency_rules(text, scores)

    normalized = _normalize(scores)

    if all(v == 0 for v in normalized.values()):
        return SentimentResult(Sentiment.NEUTRAL, 0.5,
                               {s.value: 0.0 for s in Sentiment})

    label_str = max(normalized, key=normalized.get)
    return SentimentResult(Sentiment(label_str), normalized[label_str], normalized)