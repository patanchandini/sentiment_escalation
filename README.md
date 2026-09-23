# Multilingual Sentiment Analysis & Escalation System

A FastAPI service that analyzes customer support messages across multiple languages, classifies their sentiment, detects high-risk issues, and routes them to the appropriate queue based on business rules — with a full audit trail for every escalation.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Sentiment Labels](#sentiment-labels)
- [Escalation Rules](#escalation-rules)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Example Usage](#example-usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [License](#license)
- [Author](#author)

---

## Overview

Customer support teams receive messages in many languages, with many tones, and with varying levels of urgency. Manually triaging every message is slow, and high-risk issues (like account compromise or legal threats) can easily slip past a tired human reader.

This project automates the first pass:

1. **Detects the language** of the incoming message
2. **Classifies sentiment** into six labels
3. **Detects high-risk content** via pattern matching
4. **Uses conversation history** to detect sarcasm
5. **Routes the message** to the correct queue based on rules
6. **Logs every escalation** with a full audit trail

The system **never changes business policies** — it only adjusts tone, priority, and routing.

---

## Features

- **Six sentiment labels** — positive, neutral, negative, frustrated, urgent, sarcastic
- **Confidence scoring** — every prediction includes a 0.0–1.0 confidence value
- **Multilingual support** — English, Spanish, French, German, Chinese, Japanese
- **Script-aware language detection** — CJK, Korean, Arabic, and Cyrillic detected by script first
- **High-risk detection** — account compromise, duplicate payment, legal threats
- **Context-aware sarcasm detection** — combines surface polarity with conversation history
- **Time-aware routing** — business hours, on-call queue, next-business-day scheduling
- **Automatic escalation** — repeated negatives, unresolved issues, and high-risk content
- **Audit logging** — every escalation records reason, activated condition, and summary
- **Tone adaptation** — warm, professional, apologetic, empathetic, empathetic-urgent, calm-professional
- **Policy-safe** — response tone changes; business rules never do

---

## Architecture

```
                        ┌─────────────────────┐
                        │   POST /analyze     │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Language Detection  │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Sentiment Classifier│
                        │ (lexicon + rules)   │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Risk Detector       │
                        │ (regex patterns)    │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Router (priority)   │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
     ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
     │human_escalation │  │    on_call      │  │next_business_day│
     └─────────────────┘  └─────────────────┘  └─────────────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Escalation Logger   │
                        │ (reason + condition │
                        │  + summary)         │
                        └─────────────────────┘
```

---

## Sentiment Labels

| Label | Description | Example |
|---|---|---|
| `positive` | Thanks, praise, satisfaction | "Thanks, this is great!" |
| `neutral` | Factual, no affect markers | "My order arrived yesterday." |
| `negative` | Complaints, bad experience | "This is bad." |
| `frustrated` | Repeated issues, "still", "again" | "This is broken again." |
| `urgent` | Time-sensitive requests | "I need this fixed immediately!" |
| `sarcastic` | Surface positive + negative context | "Oh great, just perfect..." |

---

## Escalation Rules

The router enforces a **fixed priority order**. Higher rules always win.

| Priority | Trigger | Activated Condition | Queue |
|---|---|---|---|
| 1 | Account compromise / duplicate payment / legal threat | `high_risk_pattern` | `human_escalation` |
| 2 | 3+ negative messages in last 5 | `repeated_negative>=3` | `human_escalation` |
| 3 | Negative conversation unresolved > 15 min | `unresolved_negative_15min` | `human_escalation` |
| 4 | Urgent + outside business hours | — | `on_call` |
| 5 | Normal negative + outside business hours | — | `next_business_day` |
| 6 | Everything else | — | `standard` |

**Business hours:** Monday–Friday, 09:00–18:00.

**Key behavior:** A calm high-risk complaint (e.g. *"I noticed an unauthorized login on my account."*) escalates to `human_escalation` **even though the sentiment is neutral**. Content matters, not just tone.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Data validation | Pydantic v2 |
| Language detection | `langdetect` + script-based heuristics |
| Sentiment analysis | Custom lexicon + rule engine |
| Risk detection | Regular expressions |
| Runtime | Python 3.10+ |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/patanchandini/sentiment_escalation.git
cd sentiment_escalation
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate.bat`
- **macOS / Linux:** `source venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Server

```bash
uvicorn app.main:app --reload --port 8080
```

Expected output:

```
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using WatchFiles
INFO:     Started server process [XXXXX]
INFO:     Application startup complete.
```

Then open:

- **Interactive API docs:** <http://127.0.0.1:8080/docs>
- **Escalation log:** <http://127.0.0.1:8080/escalations>

To stop the server: press **Ctrl + C**.

---

## API Endpoints

### `POST /analyze`

Analyze a message and route it.

**Request body:**

```json
{
  "message": {
    "text": "I was charged twice and I will call my lawyer!",
    "timestamp": "2025-01-06T10:00:00"
  },
  "history": [
    {
      "text": "This is broken again",
      "timestamp": "2025-01-06T09:55:00"
    }
  ]
}
```

**Response:**

```json
{
  "language": "en",
  "sentiment": "neutral",
  "confidence": 0.5,
  "scores": {
    "positive": 0.0,
    "neutral": 0.0,
    "negative": 0.0,
    "frustrated": 0.0,
    "urgent": 0.0,
    "sarcastic": 0.0
  },
  "risks": ["duplicate_payment", "legal_threat"],
  "queue": "human_escalation",
  "escalate": true,
  "tone": "professional",
  "scheduled_for": null,
  "escalation": {
    "reason": "High-risk issue: ['duplicate_payment', 'legal_threat']",
    "activated_condition": "high_risk_pattern",
    "summary": "This is broken again | I was charged twice and I will call my lawyer!",
    "timestamp": "2025-01-06T10:00:00"
  }
}
```

---

### `GET /escalations`

Returns every escalation recorded since the server started.

**Response:**

```json
[
  {
    "reason": "High-risk issue: ['duplicate_payment', 'legal_threat']",
    "activated_condition": "high_risk_pattern",
    "summary": "This is broken again | I was charged twice and I will call my lawyer!",
    "timestamp": "2025-01-06T10:00:00"
  }
]
```

---

## Example Usage

### Example 1 — Calm high-risk (escalates despite neutral tone)

```bash
curl -X POST http://127.0.0.1:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "I noticed an unauthorized login on my account.",
      "timestamp": "2025-01-06T10:00:00"
    },
    "history": []
  }'
```

**Expected:** `"escalate": true`, `"queue": "human_escalation"`, `"risks": ["account_compromise"]`

---

### Example 2 — Sarcasm with negative history

```bash
curl -X POST http://127.0.0.1:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "Oh great, just perfect...",
      "timestamp": "2025-01-06T10:00:00"
    },
    "history": [
      {"text": "This is broken again", "timestamp": "2025-01-06T09:55:00"},
      {"text": "Still not working",    "timestamp": "2025-01-06T09:57:00"}
    ]
  }'
```

**Expected:** `"sentiment": "sarcastic"` with confidence > 0.8

---

### Example 3 — After-hours urgent

```bash
curl -X POST http://127.0.0.1:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "I need this fixed immediately!",
      "timestamp": "2025-01-04T22:00:00"
    }
  }'
```

**Expected:** `"queue": "on_call"`, `"tone": "empathetic_urgent"`

---

### Example 4 — After-hours normal negative

```bash
curl -X POST http://127.0.0.1:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "This is bad.",
      "timestamp": "2025-01-04T20:00:00"
    }
  }'
```

**Expected:** `"queue": "next_business_day"`, `"scheduled_for": "2025-01-06T09:00:00"`

---

## Project Structure

```
sentiment_escalation/
├── app/
│   ├── __init__.py
│   ├── config.py         # Thresholds, business hours
│   ├── language.py       # Multilingual language detection
│   ├── logger.py         # Escalation audit log
│   ├── main.py           # FastAPI entrypoint and endpoints
│   ├── models.py         # Enums and Pydantic schemas
│   ├── risk.py           # High-risk pattern detector
│   ├── router.py         # Routing + escalation engine
│   ├── sentiment.py      # Six-label sentiment classifier
│   ├── time_utils.py     # Business hours logic
│   ├── tone.py           # Tone adapter
│   └── lexicons/
│       ├── __init__.py   # load_lexicon() function
│       ├── de.json       # German sentiment lexicon
│       ├── en.json       # English sentiment lexicon
│       ├── es.json       # Spanish sentiment lexicon
│       ├── fr.json       # French sentiment lexicon
│       ├── ja.json       # Japanese sentiment lexicon
│       └── zh.json       # Chinese sentiment lexicon
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How It Works

### 1. Language Detection — `language.py`

Script-based detection runs first (fast, deterministic), then falls back to `langdetect` for longer Latin-script text. Messages shorter than 40 characters default to English to avoid statistical misclassification.

### 2. Sentiment Classification — `sentiment.py`

Six-layer analysis:

1. **Lexicon scoring** — count matching terms from the language's JSON lexicon
2. **Sarcasm rules** — surface positive + negative history = sarcasm
3. **Ellipsis detection** — `"great..."` after praise is sarcastic
4. **Frustration rules** — `again`, `still`, repeated punctuation
5. **Urgency rules** — `now`, `asap`, `immediately`
6. **Normalization** — convert raw scores into probabilities summing to 1.0

### 3. Risk Detection — `risk.py`

Regex patterns match high-risk content:

- **Account compromise:** hacked, compromised, unauthorized, stolen, breach
- **Duplicate payment:** charged twice, double-charged, duplicate payment
- **Legal threat:** lawyer, attorney, sue, litigation, GDPR, FTC

### 4. Routing — `router.py`

Fixed priority order (see [Escalation Rules](#escalation-rules)). High-risk always wins. Urgent + after-hours goes to on-call. Normal negative + after-hours gets scheduled. Everything else uses tone adjustment only.

### 5. Escalation Logging — `logger.py`

Every escalation writes a record with:

- **reason** — human-readable explanation
- **activated_condition** — machine-readable trigger key
- **summary** — condensed conversation context
- **timestamp** — ISO 8601

---

## Testing

Manual smoke tests via `curl`:

```bash
# Calm high-risk — should escalate
curl -X POST http://127.0.0.1:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":{"text":"I noticed an unauthorized login","timestamp":"2025-01-06T10:00:00"}}'

# Sarcasm — should detect sarcastic sentiment
curl -X POST http://127.0.0.1:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":{"text":"Oh great, just perfect...","timestamp":"2025-01-06T10:00:00"},"history":[{"text":"broken again","timestamp":"2025-01-06T09:55:00"},{"text":"still not working","timestamp":"2025-01-06T09:57:00"}]}'

# After-hours urgent — should route to on_call
curl -X POST http://127.0.0.1:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":{"text":"I need this fixed immediately!","timestamp":"2025-01-04T22:00:00"}}'

# Check the escalation log
curl http://127.0.0.1:8080/escalations
```

For interactive testing, use the Swagger UI at `/docs`.

---

## Known Limitations

- **Risk patterns are English-only** in the current version. Non-English high-risk messages (e.g. Spanish *"me cobraron dos veces"*) do not trigger escalation. To restore multilingual coverage, extend the `RISK_PATTERNS` dictionary in `app/risk.py` with translated terms.
- **Escalation log is in-memory.** Records are lost when the server restarts. For production, persist to a database or append-only file.
- **Sarcasm detection is heuristic.** It works well on obvious cases but may miss subtle or culturally-specific sarcasm. A fine-tuned transformer model would improve accuracy.
- **Non-English lexicons are English copies.** The `es.json`, `fr.json`, `de.json`, `zh.json`, and `ja.json` files currently mirror `en.json`. Translating their term lists enables true multilingual sentiment classification.

---

## Future Improvements

- Persist escalations to SQLite or PostgreSQL
- Replace lexicon classification with a fine-tuned XLM-R model
- Add authentication to the API endpoints
- Add rate limiting to prevent abuse
- Add a `/health` endpoint for monitoring
- Write pytest tests for every escalation rule
- Add Docker + docker-compose for deployment
- Emit Prometheus metrics for escalation rate, latency, 
  sarcasm rate
---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Author

**Patan Chandini** — [@patanchandini](https://github.com/patanchandini)

Built as a demonstration of multilingual sentiment analysis combined with rule-based escalation logic for customer-support systems.

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) — modern Python web framework
- [Uvicorn](https://www.uvicorn.org/) — fast ASGI server
- [langdetect](https://github.com/Mimino666/langdetect) — port of Google's language-detection library
- [Pydantic](https://docs.pydantic.dev/) — data validation for Python

---

⭐ If you find this project useful, consider giving it a star!
