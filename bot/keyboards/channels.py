"""Channel list and channel detail keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Channel, ChannelPricing
from bot.utils.pagination import paginate_buttons
from bot.locales.i18n import get_text


def channels_list_kb(
    channels: list[Channel],
    district_id: int,
    lang: str = "uz",
    page: int = 1,
) -> InlineKeyboardMarkup:
    items = []
    for ch in channels:
        subs = ch.subscribers_count
        if subs >= 1000:
            subs_str = f"{subs / 1000:.1f}K"
        else:
            subs_str = str(subs)
        items.append(
            (f"📺 {ch.channel_title} ({subs_str})", f"channel:{ch.id}")
        )

    return paginate_buttons(
        items=items,
        page=page,
        per_page=6,
        columns=1,
        nav_prefix=f"ch_page_{district_id}",
        back_btn=(get_text("menu.back", lang), f"browse:back_to_district:{district_id}"),
    )


def channel_detail_kb(
    channel: Channel, lang: str = "uz"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_text("channel.order_btn", lang),
        callback_data=f"order:start:{channel.id}",
    )
    builder.button(
        text=get_text("menu.back", lang),
        callback_data=f"browse:back_to_channels:{channel.district_id}",
    )
    builder.adjust(1)
    return builder.as_markup()


def ad_formats_kb(
    pricing_list: list[ChannelPricing],
    channel_id: int,
    lang: str = "uz",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in pricing_list:
        fmt_name = p.ad_format.name_uz if lang == "uz" else p.ad_format.name_ru
        price_str = f"{p.price:,}".replace(",", " ")
        builder.button(
            text=f"{fmt_name} — {price_str} so'm",
            callback_data=f"order:format:{channel_id}:{p.ad_format_id}",
        )
    builder.button(
        text=get_text("menu.back", lang),
        callback_data=f"channel:{channel_id}",
    )
    builder.adjust(1)
    return builder.as_markup()
