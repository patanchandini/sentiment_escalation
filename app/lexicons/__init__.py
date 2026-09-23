import json
import pathlib

_DIR = pathlib.Path(__file__).parent
_CACHE = {}


def load_lexicon(lang: str) -> dict:
    """Load a lexicon JSON by language code. Falls back to English."""
    if lang in _CACHE:
        return _CACHE[lang]

    path = _DIR / f"{lang}.json"
    if not path.exists():
        path = _DIR / "en.json"

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    _CACHE[lang] = data
    return data