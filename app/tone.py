TONE_PREFIX = {
    "warm":              "Thanks so much for reaching out!",
    "professional":      "Thank you for your message.",
    "apologetic":        "I'm sorry for the trouble this caused.",
    "empathetic":        "I can see this has been frustrating — let's fix it.",
    "empathetic_urgent": "I understand this is time-sensitive; here's what we're doing now.",
    "calm_professional": "I hear your concern — let me address it directly.",
}

def apply_tone(tone: str, base_response: str, policy_context: str) -> str:
    """
    policy_context is READ-ONLY. We only change wording, not rules.
    """
    prefix = TONE_PREFIX.get(tone, TONE_PREFIX["professional"])
    return f"{prefix}\n\n{base_response}\n\n{policy_context}"