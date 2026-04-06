"""
Internationalization helper.
Usage: text = get_text("menu.main", lang="uz")
"""

from bot.locales.uz import TEXTS as UZ_TEXTS
from bot.locales.ru import TEXTS as RU_TEXTS
from bot.locales.en import TEXTS as EN_TEXTS
from bot.locales.uz_cyrl import TEXTS as UZ_CYRL_TEXTS
from bot.locales.tg import TEXTS as TG_TEXTS
from bot.locales.tr import TEXTS as TR_TEXTS
from bot.locales.hi import TEXTS as HI_TEXTS
from bot.locales.ar import TEXTS as AR_TEXTS
from bot.locales.kk import TEXTS as KK_TEXTS
from bot.locales.ky import TEXTS as KY_TEXTS

LANGUAGES = {
    "uz": {"texts": UZ_TEXTS, "label": "🇺🇿 O'zbekcha", "name": "O'zbekcha"},
    "ru": {"texts": RU_TEXTS, "label": "🇷🇺 Русский", "name": "Русский"},
    "en": {"texts": EN_TEXTS, "label": "🇬🇧 English", "name": "English"},
    "uz_cyrl": {"texts": UZ_CYRL_TEXTS, "label": "🇺🇿 Ўзбекча", "name": "Ўзбекча (кирилл)"},
    "tg": {"texts": TG_TEXTS, "label": "🇹🇯 Тоҷикӣ", "name": "Тоҷикӣ"},
    "tr": {"texts": TR_TEXTS, "label": "🇹🇷 Türkçe", "name": "Türkçe"},
    "hi": {"texts": HI_TEXTS, "label": "🇮🇳 हिन्दी", "name": "हिन्दी"},
    "ar": {"texts": AR_TEXTS, "label": "🇸🇦 العربية", "name": "العربية"},
    "kk": {"texts": KK_TEXTS, "label": "🇰🇿 Қазақша", "name": "Қазақша"},
    "ky": {"texts": KY_TEXTS, "label": "🇰🇬 Кыргызча", "name": "Кыргызча"},
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


def menu_match(key: str) -> set[str]:
    """Get all translations for a menu key across all languages.
    Usage: F.text.in_(menu_match("menu.browse"))
    """
    return {
        info["texts"].get(key, "")
        for info in LANGUAGES.values()
        if info["texts"].get(key)
    }
