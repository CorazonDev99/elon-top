"""
Browse handler — region → district → channels → channel detail.
Core flow for advertisers browsing the catalog.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.regions import regions_kb, districts_kb
from bot.keyboards.channels import channels_list_kb, channel_detail_kb
from bot.database.repositories import region_repo, channel_repo
from bot.utils.formatting import format_price, format_subscribers

router = Router()


async def show_regions(message: Message, lang: str = "uz", **kwargs):
    session: AsyncSession = kwargs.get("session")
    if not session:
        return
    regions = await region_repo.get_all_regions(session)
    await message.answer(
        get_text("browse.select_region", lang),
        reply_markup=regions_kb(regions, lang),
        parse_mode="HTML",
    )


# ─── Region pagination ───
@router.callback_query(F.data.startswith("reg_page:"))
async def region_page(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    page = int(callback.data.split(":")[1])
    regions = await region_repo.get_all_regions(session)
    await callback.message.edit_text(
        get_text("browse.select_region", lang),
        reply_markup=regions_kb(regions, lang, page),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Select region → show districts (or all channels) ───
@router.callback_query(F.data.startswith("region:"))
async def select_region(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    region_val = callback.data.split(":")[1]

    if region_val == "all":
        # Show ALL channels in the country
        channels = await channel_repo.get_all_active_channels(session)
        label = "O'zbekiston" if lang == "uz" else "Узбекистан"
        await _show_channels_list(callback, session, channels, label, lang, back_data="browse:back_to_regions")
        return

    region_id = int(region_val)
    region = await region_repo.get_region(session, region_id)
    districts = await region_repo.get_districts_by_region(session, region_id)

    region_name = region.name_uz if lang == "uz" else region.name_ru

    await callback.message.edit_text(
        get_text("browse.select_district", lang, region=region_name),
        reply_markup=districts_kb(districts, region_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── District pagination ───
@router.callback_query(F.data.regexp(r"^dist_page_(\d+):(\d+)$"))
async def district_page(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    parts = callback.data.split(":")
    # dist_page_REGIONID:PAGE
    region_id = int(parts[0].split("_")[-1])
    page = int(parts[1])

    region = await region_repo.get_region(session, region_id)
    districts = await region_repo.get_districts_by_region(session, region_id)
    region_name = region.name_uz if lang == "uz" else region.name_ru

    await callback.message.edit_text(
        get_text("browse.select_district", lang, region=region_name),
        reply_markup=districts_kb(districts, region_id, lang, page),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Select district → show channels ───
@router.callback_query(F.data.startswith("district:"))
async def select_district(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    district_val = callback.data.split(":")[1]

    if district_val.startswith("all_"):
        # Show all channels in this region
        region_id = int(district_val.split("_")[1])
        channels = await channel_repo.get_channels_by_region(session, region_id)
        region = await region_repo.get_region(session, region_id)
        label = region.name_uz if lang == "uz" else region.name_ru
        await _show_channels_list(callback, session, channels, label, lang, back_data="browse:back_to_regions")
        return

    district_id = int(district_val)
    await _show_channels(callback, session, district_id, lang)


async def _show_channels_list(
    callback: CallbackQuery,
    session: AsyncSession,
    channels: list,
    area_name: str,
    lang: str,
    back_data: str = "browse:back_to_regions",
    page: int = 1,
):
    """Show channels from a list (used for region-wide / country-wide views)."""
    if not channels:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.button(text=get_text("menu.back", lang), callback_data=back_data)
        builder.adjust(1)
        await callback.message.edit_text(
            get_text("browse.no_channels", lang),
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    else:
        from bot.utils.pagination import paginate_buttons
        items = []
        for ch in channels:
            subs = ch.subscribers_count
            subs_str = f"{subs / 1000:.1f}K" if subs >= 1000 else str(subs)
            items.append((f"📺 {ch.channel_title} ({subs_str})", f"channel:{ch.id}"))

        kb = paginate_buttons(
            items=items,
            page=page,
            per_page=6,
            columns=1,
            nav_prefix="ch_all_page",
            back_btn=(get_text("menu.back", lang), back_data),
        )
        await callback.message.edit_text(
            get_text("browse.channels_list", lang, district=area_name, count=len(channels)),
            reply_markup=kb,
            parse_mode="HTML",
        )
    await callback.answer()


async def _show_channels(
    callback: CallbackQuery,
    session: AsyncSession,
    district_id: int,
    lang: str,
    page: int = 1,
):
    district = await region_repo.get_district(session, district_id)
    channels = await channel_repo.get_channels_by_district(session, district_id)

    district_name = district.name_uz if lang == "uz" else district.name_ru

    if not channels:
        await callback.message.edit_text(
            get_text("browse.no_channels", lang),
            reply_markup=districts_kb(
                await region_repo.get_districts_by_region(session, district.region_id),
                district.region_id,
                lang,
            ),
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            get_text("browse.channels_list", lang, district=district_name, count=len(channels)),
            reply_markup=channels_list_kb(channels, district_id, lang, page),
            parse_mode="HTML",
        )
    await callback.answer()


# ─── Channel pagination ───
@router.callback_query(F.data.regexp(r"^ch_page_(\d+):(\d+)$"))
async def channel_page(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    parts = callback.data.split(":")
    district_id = int(parts[0].split("_")[-1])
    page = int(parts[1])
    await _show_channels(callback, session, district_id, lang, page)


# ─── Channel detail ───
@router.callback_query(F.data.startswith("ch:"))
async def show_channel_short(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    """Alias: ch:ID used from search results."""
    channel_id = int(callback.data.split(":")[1])
    await _show_channel_detail(callback, session, channel_id, lang)


@router.callback_query(F.data.startswith("channel:"))
async def show_channel(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    channel_id = int(callback.data.split(":")[1])
    await _show_channel_detail(callback, session, channel_id, lang)


async def _show_channel_detail(callback: CallbackQuery, session: AsyncSession, channel_id: int, lang: str):
    channel = await channel_repo.get_channel_full(session, channel_id)

    if not channel:
        await callback.answer("Channel not found", show_alert=True)
        return

    # Auto-update subscriber count from Telegram
    try:
        chat = await callback.bot.get_chat(f"@{channel.channel_username}")
        members = await callback.bot.get_chat_member_count(chat.id)
        if members and members != channel.subscribers_count:
            await channel_repo.update_channel_stats(session, channel_id, members)
            channel.subscribers_count = members
    except Exception:
        pass

    # Build pricing text
    pricing_text = ""
    for p in channel.pricing:
        fmt_name = p.ad_format.name_uz if lang == "uz" else p.ad_format.name_ru
        pricing_text += get_text(
            "channel.price_line", lang,
            format=fmt_name,
            price=format_price(p.price),
        )

    if not pricing_text:
        pricing_text = "—"

    if channel.district:
        district_name = channel.district.name_uz if lang == "uz" else channel.district.name_ru
        region_name = channel.district.region.name_uz if lang == "uz" else channel.district.region.name_ru
    else:
        district_name = "Butun viloyat" if lang == "uz" else "Весь регион"
        region_name = "O'zbekiston" if lang == "uz" else "Узбекистан"
    cat_name = channel.category.name_uz if lang == "uz" else channel.category.name_ru
    verified = get_text("channel.verified" if channel.is_verified else "channel.not_verified", lang)

    # Star rating display
    if channel.avg_rating > 0:
        full_stars = int(channel.avg_rating)
        rating_str = "⭐" * full_stars + f" {channel.avg_rating}/5 ({channel.rating_count})"
    else:
        rating_str = "—"

    text = get_text(
        "channel.card", lang,
        title=channel.channel_title,
        username=channel.channel_username,
        district=district_name,
        region=region_name,
        category=f"{channel.category.emoji} {cat_name}",
        subscribers=format_subscribers(channel.subscribers_count),
        views=format_subscribers(channel.avg_views),
        verified=verified,
        pricing=pricing_text,
        rating=rating_str,
    )

    # Get recommendations
    similar = await channel_repo.get_similar_channels(session, channel_id, limit=3)

    kb = channel_detail_kb(channel, lang)

    # Add recommendation buttons
    if similar:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        # Copy existing buttons from kb
        for row in kb.inline_keyboard:
            for btn in row:
                builder.button(text=btn.text, callback_data=btn.callback_data)

        builder.button(
            text=f"━━ {get_text('channel.similar', lang)} ━━",
            callback_data="noop",
        )
        for sim in similar:
            stars = f"⭐{sim.avg_rating}" if sim.avg_rating > 0 else ""
            builder.button(
                text=f"📺 {sim.channel_title} {stars}",
                callback_data=f"ch:{sim.id}",
            )
        builder.adjust(1)
        reply_markup = builder.as_markup()
    else:
        reply_markup = kb

    await callback.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Navigation: back buttons ───
@router.callback_query(F.data == "browse:back_to_regions")
async def back_to_regions(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    regions = await region_repo.get_all_regions(session)
    await callback.message.edit_text(
        get_text("browse.select_region", lang),
        reply_markup=regions_kb(regions, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("browse:back_to_district:"))
async def back_to_district(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    district_id = int(callback.data.split(":")[2])
    district = await region_repo.get_district(session, district_id)
    region = await region_repo.get_region(session, district.region_id)
    districts = await region_repo.get_districts_by_region(session, district.region_id)
    region_name = region.name_uz if lang == "uz" else region.name_ru

    await callback.message.edit_text(
        get_text("browse.select_district", lang, region=region_name),
        reply_markup=districts_kb(districts, district.region_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("browse:back_to_channels:"))
async def back_to_channels(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    district_id = int(callback.data.split(":")[2])
    await _show_channels(callback, session, district_id, lang)


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery, **kwargs):
    await callback.answer()
