"""
Features handler:
- Bulk (package) orders — select multiple channels
- Subscriptions — weekly auto-ad
- Terms acceptance
"""

from datetime import date, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text, menu_match
from bot.keyboards.main_menu import main_menu_kb, cancel_kb
from bot.database.repositories import channel_repo, order_repo, subscription_repo, user_repo
from bot.utils.formatting import format_price
from bot.config import settings

router = Router()


# ═══════════════════════════════════════════════
# TERMS ACCEPTANCE
# ═══════════════════════════════════════════════

TERMS_UZ = (
    "📝 <b>Xizmat ko'rsatish shartlari</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "1️⃣ Reklama mazmuni qonunga zid bo'lmasligi kerak\n"
    "2️⃣ Buyurtma tasdiqlangandan so'ng to'lov 24 soat ichida amalga oshirilishi kerak\n"
    "3️⃣ Kanal egasi reklamani belgilangan muddatda joylashtirishi shart\n"
    "4️⃣ Reklama 48 soat ichida joylashtirilmasa, to'lov qaytariladi\n"
    "5️⃣ Bot administratsiyasi nizolarni hal qilish huquqiga ega\n"
    "6️⃣ Kanal egasi oylik daromadning 5% komissiyasini to'laydi\n\n"
    "Davom etish uchun shartlarni qabul qiling:"
)

TERMS_RU = (
    "📝 <b>Условия использования</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "1️⃣ Содержание рекламы не должно нарушать закон\n"
    "2️⃣ Оплата должна быть произведена в течение 24 часов после подтверждения\n"
    "3️⃣ Владелец канала обязан разместить рекламу в указанный срок\n"
    "4️⃣ Если реклама не размещена в течение 48 часов, оплата возвращается\n"
    "5️⃣ Администрация бота вправе разрешать споры\n"
    "6️⃣ Владелец канала оплачивает 5% комиссию от месячного дохода\n\n"
    "Для продолжения примите условия:"
)


@router.callback_query(F.data == "terms:accept")
async def accept_terms(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    await user_repo.accept_terms(session, callback.from_user.id)
    await callback.message.edit_text(
        "✅ " + ("Shartlar qabul qilindi!" if lang == "uz" else "Условия приняты!"),
        parse_mode="HTML",
    )
    await callback.answer()


async def check_terms(message_or_callback, session, lang, user_tid) -> bool:
    """Check if user accepted terms. If not, show terms. Returns True if accepted."""
    user = await user_repo.get_user(session, user_tid)
    if user and user.terms_accepted:
        return True

    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Qabul qilaman" if lang == "uz" else "✅ Принимаю",
        callback_data="terms:accept",
    )
    builder.adjust(1)

    text = TERMS_UZ if lang == "uz" else TERMS_RU

    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.answer(
            text, reply_markup=builder.as_markup(), parse_mode="HTML",
        )
    else:
        await message_or_callback.answer(
            text, reply_markup=builder.as_markup(), parse_mode="HTML",
        )
    return False


# ═══════════════════════════════════════════════
# BULK / PACKAGE ORDERS
# ═══════════════════════════════════════════════

class BulkOrderStates(StatesGroup):
    selecting_channels = State()
    send_ad_content = State()
    select_date = State()
    preview = State()


@router.message(F.text.in_(menu_match("menu.bulk_order")))
async def start_bulk_order(
    message: Message, session: AsyncSession, state: FSMContext, lang: str = "uz", **kwargs
):
    # Check terms first
    if not await check_terms(message, session, lang, message.from_user.id):
        return

    # Get all active channels
    from bot.database.models import Channel
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload

    result = await session.execute(
        select(Channel)
        .options(joinedload(Channel.category), joinedload(Channel.pricing))
        .where(Channel.is_active == True, Channel.is_verified == True)
        .order_by(Channel.avg_rating.desc())
        .limit(30)
    )
    channels = list(result.scalars().unique().all())

    if not channels:
        await message.answer(
            get_text("browse.no_channels", lang), parse_mode="HTML",
        )
        return

    await state.set_state(BulkOrderStates.selecting_channels)
    await state.update_data(selected_channels=[], available_channels={
        ch.id: ch.channel_title for ch in channels
    })

    builder = InlineKeyboardBuilder()
    for ch in channels:
        min_price = min((p.price for p in ch.pricing), default=0) if ch.pricing else 0
        builder.button(
            text=f"📺 {ch.channel_title} ({format_price(min_price)})",
            callback_data=f"bulk:toggle:{ch.id}",
        )
    builder.button(text="✅ Davom etish" if lang == "uz" else "✅ Продолжить", callback_data="bulk:done")
    builder.adjust(1)

    await message.answer(
        get_text("bulk.select_channels", lang),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("bulk:toggle:"), BulkOrderStates.selecting_channels)
async def toggle_bulk_channel(
    callback: CallbackQuery, state: FSMContext, lang: str = "uz", **kwargs
):
    channel_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    selected = data.get("selected_channels", [])

    if channel_id in selected:
        selected.remove(channel_id)
        await callback.answer(f"❌ Olib tashlandi" if lang == "uz" else "❌ Убрано")
    else:
        selected.append(channel_id)
        await callback.answer(f"✅ Qo'shildi ({len(selected)} ta)" if lang == "uz" else f"✅ Добавлено ({len(selected)})")

    await state.update_data(selected_channels=selected)

    # Update button text to show selection
    available = data.get("available_channels", {})
    builder = InlineKeyboardBuilder()
    for ch_id, title in available.items():
        mark = "✅" if ch_id in selected else "📺"
        builder.button(
            text=f"{mark} {title}",
            callback_data=f"bulk:toggle:{ch_id}",
        )
    count_text = f" ({len(selected)} ta)" if selected else ""
    builder.button(
        text=("✅ Davom etish" if lang == "uz" else "✅ Продолжить") + count_text,
        callback_data="bulk:done",
    )
    builder.adjust(1)

    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(F.data == "bulk:done", BulkOrderStates.selecting_channels)
async def bulk_done_selecting(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext, lang: str = "uz", **kwargs
):
    data = await state.get_data()
    selected = data.get("selected_channels", [])

    if len(selected) < 2:
        await callback.answer(
            "Kamida 2 ta kanal tanlang!" if lang == "uz" else "Выберите минимум 2 канала!",
            show_alert=True,
        )
        return

    # Calculate total price with 15% discount
    from bot.database.models import Channel, ChannelPricing
    from sqlalchemy import select as sql_select

    total = 0
    channel_names = []
    for ch_id in selected:
        result = await session.execute(
            sql_select(ChannelPricing).where(ChannelPricing.channel_id == ch_id)
        )
        prices = list(result.scalars().all())
        if prices:
            total += min(p.price for p in prices)

        ch_result = await session.execute(
            sql_select(Channel).where(Channel.id == ch_id)
        )
        ch = ch_result.scalar_one_or_none()
        if ch:
            channel_names.append(ch.channel_title)

    discount = int(total * 0.15)
    final = total - discount

    await state.update_data(
        bulk_total=total, bulk_discount=discount, bulk_final=final,
        bulk_channel_names=channel_names,
    )
    await state.set_state(BulkOrderStates.send_ad_content)

    text = get_text(
        "bulk.summary", lang,
        count=len(selected),
        channels="\n".join(f"  📺 {n}" for n in channel_names),
        total=format_price(total),
        discount=format_price(discount),
        final=format_price(final),
    )

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.message.answer(
        get_text("order.enter_text", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ═══════════════════════════════════════════════
# SUBSCRIPTIONS
# ═══════════════════════════════════════════════

@router.message(F.text.in_(menu_match("menu.subscriptions")))
async def show_subscriptions(
    message: Message, session: AsyncSession, lang: str = "uz", **kwargs
):
    subs = await subscription_repo.get_user_subscriptions(session, message.from_user.id)

    if not subs:
        text = get_text("sub.empty", lang)
    else:
        text = get_text("sub.title", lang) + "\n\n"
        for s in subs:
            status = "✅" if s.is_active else "⏸"
            ch_name = s.channel.channel_title if s.channel else "—"
            freq_name = {"weekly": "📅 Haftalik", "biweekly": "📅 2 haftalik", "monthly": "📅 Oylik"}.get(
                s.frequency, s.frequency
            ) if lang == "uz" else {"weekly": "📅 Еженедельно", "biweekly": "📅 Раз в 2 недели", "monthly": "📅 Ежемесячно"}.get(
                s.frequency, s.frequency
            )
            text += (
                f"{status} <b>{ch_name}</b>\n"
                f"   {freq_name} • {format_price(s.price_per_post)} so'm\n"
                f"   Jami postlar: {s.total_posts}\n\n"
            )

    builder = InlineKeyboardBuilder()
    for s in (subs or []):
        if s.is_active:
            builder.button(
                text=f"⏸ {s.channel.channel_title}" if s.channel else f"⏸ #{s.id}",
                callback_data=f"sub:cancel:{s.id}",
            )
    builder.adjust(1)

    await message.answer(
        text,
        reply_markup=builder.as_markup() if subs else None,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("sub:cancel:"))
async def cancel_sub(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    sub_id = int(callback.data.split(":")[2])
    await subscription_repo.cancel_subscription(session, sub_id)
    await callback.message.edit_text(
        "✅ " + ("Obuna bekor qilindi." if lang == "uz" else "Подписка отменена."),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sub:create:"))
async def create_sub_from_order(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    """Create subscription from a completed order."""
    order_id = int(callback.data.split(":")[2])
    order = await order_repo.get_order(session, order_id)
    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    freq_builder = InlineKeyboardBuilder()
    freq_builder.button(text="📅 Haftalik" if lang == "uz" else "📅 Еженедельно",
                       callback_data=f"sub:freq:{order_id}:weekly")
    freq_builder.button(text="📅 2 hafta" if lang == "uz" else "📅 Раз в 2 нед.",
                       callback_data=f"sub:freq:{order_id}:biweekly")
    freq_builder.button(text="📅 Oylik" if lang == "uz" else "📅 Ежемесячно",
                       callback_data=f"sub:freq:{order_id}:monthly")
    freq_builder.adjust(3)

    await callback.message.answer(
        get_text("sub.select_frequency", lang),
        reply_markup=freq_builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sub:freq:"))
async def set_sub_frequency(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    parts = callback.data.split(":")
    order_id = int(parts[2])
    frequency = parts[3]

    order = await order_repo.get_order(session, order_id)
    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    sub = await subscription_repo.create_subscription(
        session,
        advertiser_tid=order.advertiser_telegram_id,
        channel_id=order.channel_id,
        ad_format_id=order.ad_format_id,
        price=order.price,
        frequency=frequency,
        ad_text=order.ad_text,
        ad_media_file_id=order.ad_media_file_id,
        ad_media_type=order.ad_media_type,
    )

    freq_name = {"weekly": "haftalik", "biweekly": "2 haftalik", "monthly": "oylik"}.get(frequency, frequency)
    if lang == "ru":
        freq_name = {"weekly": "еженедельно", "biweekly": "раз в 2 недели", "monthly": "ежемесячно"}.get(frequency, frequency)

    await callback.message.edit_text(
        get_text("sub.created", lang, frequency=freq_name, price=format_price(order.price)),
        parse_mode="HTML",
    )
    await callback.answer()
