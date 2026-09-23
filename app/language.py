import re
from langdetect import detect, LangDetectException

CJK_PATTERN      = re.compile(r"[\u4e00-\u9fff]")
HIRAGANA_KATA    = re.compile(r"[\u3040-\u30ff]")
HANGUL_PATTERN   = re.compile(r"[\uac00-\ud7af]")
ARABIC_PATTERN   = re.compile(r"[\u0600-\u06ff]")
CYRILLIC_PATTERN = re.compile(r"[\u0400-\u04ff]")

MIN_LENGTH_FOR_DETECT = 40


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "en"

    if CJK_PATTERN.search(text):      return "zh"
    if HIRAGANA_KATA.search(text):    return "ja"
    if HANGUL_PATTERN.search(text):   return "ko"
    if ARABIC_PATTERN.search(text):   return "ar"
    if CYRILLIC_PATTERN.search(text): return "ru"

    stripped = text.strip()
    if len(stripped) <= MIN_LENGTH_FOR_DETECT:
        return "en"

    try:
        return detect(stripped)
    except LangDetectException:
        return "en"