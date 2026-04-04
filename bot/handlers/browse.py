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


# ─── Select region → show districts ───
@router.callback_query(F.data.startswith("region:"))
async def select_region(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    region_id = int(callback.data.split(":")[1])
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
    district_id = int(callback.data.split(":")[1])
    await _show_channels(callback, session, district_id, lang)


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
@router.callback_query(F.data.startswith("channel:"))
async def show_channel(callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs):
    channel_id = int(callback.data.split(":")[1])
    channel = await channel_repo.get_channel_full(session, channel_id)

    if not channel:
        await callback.answer("Channel not found", show_alert=True)
        return

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

    district_name = channel.district.name_uz if lang == "uz" else channel.district.name_ru
    region_name = channel.district.region.name_uz if lang == "uz" else channel.district.region.name_ru
    cat_name = channel.category.name_uz if lang == "uz" else channel.category.name_ru
    verified = get_text("channel.verified" if channel.is_verified else "channel.not_verified", lang)

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
    )

    await callback.message.edit_text(
        text,
        reply_markup=channel_detail_kb(channel, lang),
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
