"""Generic inline keyboard pagination utility."""

import math
from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def paginate_buttons(
    items: list[tuple[str, str]],  # (text, callback_data)
    page: int = 1,
    per_page: int = 8,
    columns: int = 2,
    nav_prefix: str = "page",
    back_btn: tuple[str, str] | None = None,  # (text, callback_data)
) -> InlineKeyboardMarkup:
    """
    Create a paginated inline keyboard.

    Args:
        items: list of (button_text, callback_data) tuples
        page: current page (1-indexed)
        per_page: items per page
        columns: buttons per row
        nav_prefix: prefix for pagination callback data
        back_btn: optional back button at the bottom
    """
    builder = InlineKeyboardBuilder()

    total_pages = max(1, math.ceil(len(items) / per_page))
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]

    # Add item buttons
    for text, callback_data in page_items:
        builder.button(text=text, callback_data=callback_data)

    # Arrange in columns
    builder.adjust(columns)

    # Navigation row
    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="◀️", callback_data=f"{nav_prefix}:{page - 1}"
                )
            )
        nav_buttons.append(
            InlineKeyboardButton(
                text=f"📄 {page}/{total_pages}", callback_data="noop"
            )
        )
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="▶️", callback_data=f"{nav_prefix}:{page + 1}"
                )
            )
        builder.row(*nav_buttons)

    # Back button
    if back_btn:
        builder.row(
            InlineKeyboardButton(text=back_btn[0], callback_data=back_btn[1])
        )

    return builder.as_markup()
