"""Order-related keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales.i18n import get_text


def order_confirm_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("order.confirm", lang), callback_data="order:confirm")
    builder.button(text=get_text("order.cancel", lang), callback_data="order:cancel")
    builder.adjust(2)
    return builder.as_markup()


def order_action_kb(
    order_id: int, lang: str = "uz", for_owner: bool = False
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if for_owner:
        builder.button(
            text=get_text("owner.accept_order", lang),
            callback_data=f"owner_order:accept:{order_id}",
        )
        builder.button(
            text=get_text("owner.reject_order", lang),
            callback_data=f"owner_order:reject:{order_id}",
        )
    else:
        builder.button(
            text=get_text("my_orders.cancel_btn", lang),
            callback_data=f"my_order:cancel:{order_id}",
        )
    builder.adjust(2)
    return builder.as_markup()


def payment_kb(order_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💳 " + get_text("order.confirm", lang),
        callback_data=f"payment:send:{order_id}",
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_payment_kb(order_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_text("admin.confirm_payment", lang),
        callback_data=f"admin_pay:confirm:{order_id}",
    )
    builder.button(
        text=get_text("admin.reject_payment", lang),
        callback_data=f"admin_pay:reject:{order_id}",
    )
    builder.adjust(2)
    return builder.as_markup()


def owner_published_kb(order_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_text("owner.mark_published", lang),
        callback_data=f"owner_order:published:{order_id}",
    )
    builder.adjust(1)
    return builder.as_markup()
