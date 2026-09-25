"""
Test suite for the sentiment escalation system.

Run with:
    pytest tests/ -v
"""

from datetime import datetime

from app.models import Sentiment, HistoryMessage
from app.sentiment import analyze_sentiment
from app.risk import detect_risks, Risk
from app.router import Router


# ---------------------------------------------------------------
# Risk detection
# ---------------------------------------------------------------

def test_risk_account_compromise():
    assert Risk.ACCOUNT_COMPROMISE in detect_risks(
        "Someone hacked my account"
    )


def test_risk_duplicate_payment():
    assert Risk.DUPLICATE_PAYMENT in detect_risks(
        "I was charged twice for the same order"
    )


def test_risk_legal_threat():
    assert Risk.LEGAL_THREAT in detect_risks(
        "I will take you to court"
    )


def test_risk_none_for_benign_message():
    assert detect_risks("Hello, how are you?") == []


def test_risk_multiple_categories():
    risks = detect_risks(
        "My account was hacked and I will call my lawyer"
    )
    assert Risk.ACCOUNT_COMPROMISE in risks
    assert Risk.LEGAL_THREAT in risks


# ---------------------------------------------------------------
# Sentiment classification
# ---------------------------------------------------------------

def test_sentiment_positive():
    r = analyze_sentiment("Thanks, this is great!", "en", [])
    assert r.label == Sentiment.POSITIVE


def test_sentiment_negative():
    r = analyze_sentiment("This is bad.", "en", [])
    assert r.label == Sentiment.NEGATIVE


def test_sentiment_urgent():
    r = analyze_sentiment(
        "I need this fixed immediately!", "en", []
    )
    assert r.label == Sentiment.URGENT


def test_sentiment_sarcasm_with_negative_history():
    history = [
        HistoryMessage(
            text="This is broken again",
            timestamp=datetime(2025, 1, 6, 9, 55),
        ),
        HistoryMessage(
            text="Still not working",
            timestamp=datetime(2025, 1, 6, 9, 57),
        ),
    ]
    r = analyze_sentiment("Oh great, just perfect...", "en", history)
    assert r.label == Sentiment.SARCASTIC
    assert r.confidence > 0.5


def test_sentiment_confidence_range():
    r = analyze_sentiment("This is terrible", "en", [])
    assert 0.0 <= r.confidence <= 1.0


# ---------------------------------------------------------------
# Router — high-risk escalation
# ---------------------------------------------------------------

def test_router_calm_high_risk_escalates():
    """Calm tone + high-risk content must still escalate."""
    router = Router()
    text = "I noticed an unauthorized login on my account."
    sentiment = analyze_sentiment(text, "en", [])
    risks = detect_risks(text)
    decision = router.route(
        text, sentiment, risks, [], datetime(2025, 1, 6, 10, 0)
    )
    assert decision["escalate"] is True
    assert decision["queue"].value == "human_escalation"
    assert decision["escalation"]["activated_condition"] == "high_risk_pattern"


def test_router_duplicate_payment_escalates():
    router = Router()
    text = "I was charged twice!"
    sentiment = analyze_sentiment(text, "en", [])
    risks = detect_risks(text)
    decision = router.route(
        text, sentiment, risks, [], datetime(2025, 1, 6, 10, 0)
    )
    assert decision["escalate"] is True
    assert decision["queue"].value == "human_escalation"


# ---------------------------------------------------------------
# Router — repeated negatives
# ---------------------------------------------------------------

def test_router_repeated_negatives_escalate():
    router = Router()
    history = [
        HistoryMessage(text="bad", timestamp=datetime(2025, 1, 6, 9, 50)),
        HistoryMessage(text="terrible", timestamp=datetime(2025, 1, 6, 9, 52)),
        HistoryMessage(text="worst", timestamp=datetime(2025, 1, 6, 9, 54)),
    ]
    text = "This is still broken"
    sentiment = analyze_sentiment(text, "en", history)
    decision = router.route(
        text, sentiment, [], history, datetime(2025, 1, 6, 10, 0)
    )
    assert decision["escalate"] is True
    assert decision["escalation"]["activated_condition"] == "repeated_negative>=3"


# ---------------------------------------------------------------
# Router — business-hours logic
# ---------------------------------------------------------------

def test_router_after_hours_urgent_goes_on_call():
    """Saturday 22:00 + urgent → on_call queue."""
    router = Router()
    text = "I need this fixed immediately!"
    sentiment = analyze_sentiment(text, "en", [])
    decision = router.route(
        text, sentiment, [], [], datetime(2025, 1, 4, 22, 0)
    )
    assert decision["queue"].value == "on_call"
    assert decision["tone"] == "empathetic_urgent"


def test_router_after_hours_normal_negative_scheduled():
    """Saturday 20:00 + normal negative → next business day."""
    router = Router()
    text = "This is bad."
    sentiment = analyze_sentiment(text, "en", [])
    decision = router.route(
        text, sentiment, [], [], datetime(2025, 1, 4, 20, 0)
    )
    assert decision["queue"].value == "next_business_day"
    assert decision["scheduled_for"] is not None
    assert "2025-01-06" in decision["scheduled_for"]


def test_router_business_hours_standard():
    """Monday 10:00 + neutral → standard queue."""
    router = Router()
    text = "My order arrived yesterday."
    sentiment = analyze_sentiment(text, "en", [])
    decision = router.route(
        text, sentiment, [], [], datetime(2025, 1, 6, 10, 0)
    )
    assert decision["queue"].value == "standard"
    assert decision["escalate"] is False


# ---------------------------------------------------------------
# Escalation log
# ---------------------------------------------------------------

def test_escalation_log_records_reason_condition_summary():
    router = Router()
    text = "I will sue you"
    sentiment = analyze_sentiment(text, "en", [])
    risks = detect_risks(text)
    router.route(text, sentiment, risks, [], datetime(2025, 1, 6, 10, 0))
    assert len(router.log.entries) == 1
    entry = router.log.entries[0]
    assert entry.reason
    assert entry.activated_condition
    assert entry.summary