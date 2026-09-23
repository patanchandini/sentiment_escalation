from datetime import datetime
from fastapi import FastAPI
from app.models import AnalyzeRequest, AnalyzeResponse
from app.language import detect_language
from app.sentiment import analyze_sentiment
from app.risk import detect_risks
from app.router import Router

app = FastAPI(title="Sentiment & Escalation Service")
router = Router()

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    now = req.message.timestamp or datetime.utcnow()
    lang = detect_language(req.message.text)

    sentiment = analyze_sentiment(
        req.message.text, lang, req.history)

    risks = detect_risks(req.message.text)

    decision = router.route(
        text=req.message.text,
        sentiment=sentiment,
        risks=risks,
        history=req.history,
        now=now,
    )

    return AnalyzeResponse(
        language=lang,
        sentiment=sentiment.label.value,
        confidence=sentiment.confidence,
        scores=sentiment.scores,
        risks=[r.value for r in risks],
        queue=decision["queue"].value,
        escalate=decision["escalate"],
        tone=decision["tone"],
        scheduled_for=decision["scheduled_for"],
        escalation=decision["escalation"],
    )

@app.get("/escalations")
def list_escalations():
    return [e.__dict__ for e in router.log.entries]