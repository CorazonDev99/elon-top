"""Admin panel keyboards."""

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Channel
from bot.locales.i18n import get_text


def admin_menu_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text("admin.stats", lang)),
                KeyboardButton(text=get_text("admin.moderate", lang)),
            ],
            [
                KeyboardButton(text=get_text("admin.broadcast", lang)),
                KeyboardButton(text=get_text("admin.all_orders", lang)),
            ],
            [
                KeyboardButton(text=get_text("menu.home", lang)),
            ],
        ],
        resize_keyboard=True,
    )


def moderate_channel_kb(
    channel_id: int, lang: str = "uz"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_text("admin.approve_channel", lang),
        callback_data=f"admin_mod:approve:{channel_id}",
    )
    builder.button(
        text=get_text("admin.reject_channel", lang),
        callback_data=f"admin_mod:reject:{channel_id}",
    )
    builder.adjust(2)
    return builder.as_markup()


def language_select_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="lang:uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang:ru")
    builder.adjust(2)
    return builder.as_markup()


def confirm_broadcast_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("confirm_yes", lang), callback_data="broadcast:confirm")
    builder.button(text=get_text("confirm_no", lang), callback_data="broadcast:cancel")
    builder.adjust(2)
    return builder.as_markup()
