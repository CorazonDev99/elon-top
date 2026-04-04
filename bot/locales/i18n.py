"""
Internationalization helper.
Usage: text = get_text("menu.main", lang="uz")
"""

from bot.locales.uz import TEXTS as UZ_TEXTS
from bot.locales.ru import TEXTS as RU_TEXTS

LANGUAGES = {
    "uz": {"texts": UZ_TEXTS, "label": "🇺🇿 O'zbekcha", "name": "O'zbekcha"},
    "ru": {"texts": RU_TEXTS, "label": "🇷🇺 Русский", "name": "Русский"},
}

DEFAULT_LANG = "uz"


def get_text(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Get localized text by key. Supports format substitution via kwargs."""
    texts = LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANG])["texts"]
    text = texts.get(key, UZ_TEXTS.get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_lang_label(lang: str) -> str:
    """Get language label for display."""
    return LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANG])["label"]


def available_languages() -> list[tuple[str, str]]:
    """Return list of (code, label) tuples."""
    return [(code, info["label"]) for code, info in LANGUAGES.items()]
