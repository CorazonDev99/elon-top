"""Region and district inline keyboards."""

from bot.database.models import Region, District
from bot.utils.pagination import paginate_buttons
from bot.locales.i18n import get_text

from aiogram.types import InlineKeyboardMarkup


def regions_kb(regions: list[Region], lang: str = "uz", page: int = 1) -> InlineKeyboardMarkup:
    items = []

    # "All of Uzbekistan" option at the top
    all_label = "🇺🇿 Butun O'zbekiston" if lang == "uz" else "🇺🇿 Вся Республика"
    items.append((all_label, "region:all"))

    for r in regions:
        name = r.name_uz if lang == "uz" else r.name_ru
        items.append((f"{r.emoji} {name}", f"region:{r.id}"))

    return paginate_buttons(
        items=items,
        page=page,
        per_page=10,
        columns=1,
        nav_prefix="reg_page",
    )


def districts_kb(
    districts: list[District],
    region_id: int,
    lang: str = "uz",
    page: int = 1,
) -> InlineKeyboardMarkup:
    items = []

    # "Entire region" option at the top
    all_label = "📍 Butun viloyat" if lang == "uz" else "📍 Весь регион"
    items.append((all_label, f"district:all_{region_id}"))

    for d in districts:
        name = d.name_uz if lang == "uz" else d.name_ru
        items.append((f"📍 {name}", f"district:{d.id}"))

    return paginate_buttons(
        items=items,
        page=page,
        per_page=8,
        columns=2,
        nav_prefix=f"dist_page_{region_id}",
        back_btn=(get_text("menu.back", lang), "browse:back_to_regions"),
    )
