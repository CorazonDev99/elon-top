"""Main menu reply keyboard."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.locales.i18n import get_text


def main_menu_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text("menu.browse", lang)),
                KeyboardButton(text=get_text("menu.search", lang)),
            ],
            [
                KeyboardButton(text=get_text("menu.my_orders", lang)),
                KeyboardButton(text=get_text("menu.my_channels", lang)),
            ],
            [
                KeyboardButton(text=get_text("menu.bulk_order", lang)),
                KeyboardButton(text=get_text("menu.settings", lang)),
            ],
            [
                KeyboardButton(text=get_text("menu.about", lang)),
            ],
        ],
        resize_keyboard=True,
    )


def settings_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text("menu.language", lang)),
            ],
            [
                KeyboardButton(text=get_text("menu.home", lang)),
            ],
        ],
        resize_keyboard=True,
    )


def cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text("menu.cancel", lang))],
        ],
        resize_keyboard=True,
    )
