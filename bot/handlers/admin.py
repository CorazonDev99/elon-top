"""
Admin handler — statistics, channel moderation, broadcast, payment confirmations.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text, menu_match
from bot.keyboards.main_menu import main_menu_kb, cancel_kb
from bot.keyboards.admin import admin_menu_kb, moderate_channel_kb, confirm_broadcast_kb
from bot.states.admin_states import AdminStates
from bot.database.repositories import channel_repo, order_repo, user_repo
from bot.utils.formatting import format_price
from bot.config import settings

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


# ─── Admin Entry ───
@router.message(F.text == "/admin")
async def cmd_admin(message: Message, lang: str = "uz", **kwargs):
    if not is_admin(message.from_user.id):
        await message.answer(get_text("access_denied", lang), parse_mode="HTML")
        return

    await message.answer(
        "🔐 <b>Admin panel</b>" if lang == "uz" else "🔐 <b>Админ-панель</b>",
        reply_markup=admin_menu_kb(lang),
        parse_mode="HTML",
    )


# ─── Stats ───
@router.message(F.text.in_(menu_match("admin.stats")))
async def show_stats(message: Message, session: AsyncSession, lang: str = "uz", **kwargs):
    if not is_admin(message.from_user.id):
        await message.answer(get_text("access_denied", lang), parse_mode="HTML")
        return

    users_count = await user_repo.count_users(session)
    channels_data = await channel_repo.count_channels(session)
    orders_data = await order_repo.count_orders(session)

    if lang == "uz":
        stats = (
            f"📊 <b>Statistika:</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{users_count}</b>\n"
            f"📺 Kanallar: <b>{channels_data['channels']}</b>\n"
            f"👥 Guruhlar: <b>{channels_data['groups']}</b>\n"
            f"  ├ ✅ Tasdiqlangan: <b>{channels_data['verified']}</b>\n"
            f"  └ ⏳ Kutilmoqda: <b>{channels_data['pending']}</b>\n"
            f"📋 Buyurtmalar: <b>{orders_data['total']}</b>\n"
            f"  ├ Bugun: <b>{orders_data['today']}</b>\n"
            f"  └ Bu hafta: <b>{orders_data['week']}</b>"
        )
    else:
        stats = (
            f"📊 <b>Статистика:</b>\n\n"
            f"👥 Пользователи: <b>{users_count}</b>\n"
            f"📺 Каналы: <b>{channels_data['channels']}</b>\n"
            f"👥 Группы: <b>{channels_data['groups']}</b>\n"
            f"  ├ ✅ Подтверждено: <b>{channels_data['verified']}</b>\n"
            f"  └ ⏳ Ожидание: <b>{channels_data['pending']}</b>\n"
            f"📋 Заказы: <b>{orders_data['total']}</b>\n"
            f"  ├ Сегодня: <b>{orders_data['today']}</b>\n"
            f"  └ На этой неделе: <b>{orders_data['week']}</b>"
        )

    await message.answer(
        stats,
        reply_markup=admin_menu_kb(lang),
        parse_mode="HTML",
    )


# ─── Moderation ───
@router.message(F.text.in_(menu_match("admin.moderate")))
async def show_moderation(message: Message, session: AsyncSession, lang: str = "uz", **kwargs):
    if not is_admin(message.from_user.id):
        await message.answer(get_text("access_denied", lang), parse_mode="HTML")
        return

    pending = await channel_repo.get_pending_channels(session)

    if not pending:
        await message.answer(
            get_text("admin.no_pending", lang), parse_mode="HTML"
        )
        return

    await message.answer(
        get_text("admin.moderate_list", lang), parse_mode="HTML"
    )

    for ch in pending:
        text = (
            f"📺 @{ch.channel_username}\n"
            f"👥 {ch.subscribers_count} obunachi\n"
            f"📂 {ch.category.emoji} {ch.category.name_uz}\n"
            f"👤 Egasi: {ch.owner.full_name or '—'}"
        )
        await message.answer(
            text,
            reply_markup=moderate_channel_kb(ch.id, lang),
            parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("admin_mod:approve:"))
async def approve_channel(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("access_denied", lang), show_alert=True)
        return

    channel_id = int(callback.data.split(":")[2])
    await channel_repo.verify_channel(session, channel_id, True)

    channel = await channel_repo.get_channel_full(session, channel_id)

    await callback.message.edit_text(
        get_text("admin.channel_approved", lang), parse_mode="HTML"
    )

    # Notify owner
    if channel and channel.owner:
        try:
            owner_lang = channel.owner.language or "uz"
            await callback.bot.send_message(
                chat_id=channel.owner.telegram_id,
                text=get_text(
                    "notify.channel_approved",
                    owner_lang,
                    title=channel.channel_title,
                    username=channel.channel_username,
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    # Auto-post to bot channel
    if channel and settings.bot_channel_id:
        try:
            subs = channel.subscribers_count or 0
            cat = f"{channel.category.emoji} {channel.category.name_uz}" if channel.category else ""
            await callback.bot.send_message(
                chat_id=settings.bot_channel_id,
                text=(
                    f"🆕 <b>Yangi kanal qo'shildi!</b>\n\n"
                    f"📺 <b>{channel.channel_title}</b>\n"
                    f"👤 @{channel.channel_username}\n"
                    f"👥 {subs:,} obunachi\n"
                    f"📂 {cat}\n\n"
                    f"📢 Reklama berish uchun @oson_reklama_uz_bot"
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    await callback.answer()


@router.callback_query(F.data.startswith("admin_mod:reject:"))
async def reject_channel(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("access_denied", lang), show_alert=True)
        return

    channel_id = int(callback.data.split(":")[2])
    channel = await channel_repo.get_channel_full(session, channel_id)

    # Delete channel
    await channel_repo.delete_channel(session, channel_id)

    await callback.message.edit_text(
        get_text("admin.channel_rejected", lang), parse_mode="HTML"
    )

    # Notify owner
    if channel and channel.owner:
        try:
            owner_lang = channel.owner.language or "uz"
            await callback.bot.send_message(
                chat_id=channel.owner.telegram_id,
                text=get_text(
                    "notify.channel_rejected",
                    owner_lang,
                    title=channel.channel_title,
                    username=channel.channel_username,
                    reason="Admin tomonidan rad etildi",
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    await callback.answer()


# ─── Broadcast ───
@router.message(F.text.in_(menu_match("admin.broadcast")))
async def start_broadcast(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    if not is_admin(message.from_user.id):
        await message.answer(get_text("access_denied", lang), parse_mode="HTML")
        return

    await state.set_state(AdminStates.broadcast_text)
    await message.answer(
        get_text("admin.broadcast_text", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )


@router.message(AdminStates.broadcast_text)
async def broadcast_text(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    # Determine what content was sent
    broadcast_data = {}

    if message.photo:
        broadcast_data["media_type"] = "photo"
        broadcast_data["media_file_id"] = message.photo[-1].file_id
        broadcast_data["caption"] = message.caption or ""
    elif message.video:
        broadcast_data["media_type"] = "video"
        broadcast_data["media_file_id"] = message.video.file_id
        broadcast_data["caption"] = message.caption or ""
    elif message.document:
        broadcast_data["media_type"] = "document"
        broadcast_data["media_file_id"] = message.document.file_id
        broadcast_data["caption"] = message.caption or ""
    elif message.text:
        broadcast_data["media_type"] = "text"
        broadcast_data["text"] = message.text
    else:
        await message.answer(
            "⚠️ Faqat matn, rasm, video yoki fayl yuboring.",
            parse_mode="HTML",
        )
        return

    users = await user_repo.get_all_users(session)
    broadcast_data["user_count"] = len(users)

    await state.update_data(**broadcast_data)
    await state.set_state(AdminStates.broadcast_confirm)

    await message.answer(
        get_text("admin.broadcast_confirm", lang, count=len(users)),
        reply_markup=confirm_broadcast_kb(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "broadcast:confirm", AdminStates.broadcast_confirm)
async def broadcast_confirm(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    data = await state.get_data()
    media_type = data.get("media_type", "text")
    users = await user_repo.get_all_users(session)

    await state.clear()
    await callback.message.edit_text("⏳ Yuborilmoqda...", parse_mode="HTML")

    sent = 0
    for user in users:
        try:
            if media_type == "photo":
                await callback.bot.send_photo(
                    chat_id=user.telegram_id,
                    photo=data["media_file_id"],
                    caption=data.get("caption", ""),
                    parse_mode="HTML",
                )
            elif media_type == "video":
                await callback.bot.send_video(
                    chat_id=user.telegram_id,
                    video=data["media_file_id"],
                    caption=data.get("caption", ""),
                    parse_mode="HTML",
                )
            elif media_type == "document":
                await callback.bot.send_document(
                    chat_id=user.telegram_id,
                    document=data["media_file_id"],
                    caption=data.get("caption", ""),
                    parse_mode="HTML",
                )
            else:
                await callback.bot.send_message(
                    chat_id=user.telegram_id,
                    text=data.get("text", ""),
                    parse_mode="HTML",
                )
            sent += 1
        except Exception:
            pass

    await callback.message.answer(
        get_text("admin.broadcast_done", lang, sent=sent, total=len(users)),
        reply_markup=admin_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast:cancel")
async def broadcast_cancel(
    callback: CallbackQuery, state: FSMContext, lang: str = "uz", **kwargs
):
    await state.clear()
    await callback.message.edit_text(
        get_text("cancelled", lang), parse_mode="HTML"
    )
    await callback.answer()


# ─── Payment confirmations (by CHANNEL OWNER) ───
@router.callback_query(F.data.startswith("admin_pay:confirm:"))
async def confirm_payment(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    order_id = int(callback.data.split(":")[2])
    order = await order_repo.get_order(session, order_id)

    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    await order_repo.update_order_status(session, order_id, "paid")

    await callback.message.edit_caption(
        caption=f"✅ Buyurtma #{order_id} to'lovi tasdiqlandi.",
    )

    # Notify advertiser
    try:
        adv_lang = order.advertiser.language or "uz"
        await callback.bot.send_message(
            chat_id=order.advertiser_telegram_id,
            text=get_text("payment.confirmed", adv_lang),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # ─── AUTO-PUBLISH to channel ───
    channel_username = order.channel.channel_username
    published = False

    try:
        chat = await callback.bot.get_chat(f"@{channel_username}")
        bot_member = await callback.bot.get_chat_member(chat.id, callback.bot.id)

        if bot_member.status in ("administrator", "creator"):
            if order.ad_media_file_id:
                media_type = order.ad_media_type or "photo"
                if media_type == "photo":
                    await callback.bot.send_photo(
                        chat_id=chat.id,
                        photo=order.ad_media_file_id,
                        caption=order.ad_text or "",
                        parse_mode="HTML",
                    )
                elif media_type == "video":
                    await callback.bot.send_video(
                        chat_id=chat.id,
                        video=order.ad_media_file_id,
                        caption=order.ad_text or "",
                        parse_mode="HTML",
                    )
                elif media_type == "document":
                    await callback.bot.send_document(
                        chat_id=chat.id,
                        document=order.ad_media_file_id,
                        caption=order.ad_text or "",
                        parse_mode="HTML",
                    )
            elif order.ad_text:
                await callback.bot.send_message(
                    chat_id=chat.id,
                    text=order.ad_text,
                    parse_mode="HTML",
                )

            published = True
            await order_repo.update_order_status(session, order_id, "published")

            # Set up recurring publish schedule
            from datetime import date as date_type, timedelta
            duration = order.ad_format.duration_days if order.ad_format else 1
            today = date_type.today()
            order.publish_start_date = today
            order.publish_end_date = today + timedelta(days=duration - 1)
            order.last_published_at = today
            order.publish_count = 1
            await session.commit()
    except Exception:
        pass

    # Notify about publish status
    if published:
        await callback.message.answer(
            f"📢 Reklama @{channel_username} kanaliga avtomatik chop etildi! ✅",
            parse_mode="HTML",
        )
    else:
        from bot.keyboards.order import owner_published_kb

        await callback.message.answer(
            (
                f"⚠️ Bot kanalda admin emas.\n"
                f"Iltimos, reklamani o'zingiz chop eting va tugmani bosing."
            ),
            reply_markup=owner_published_kb(order_id, lang),
            parse_mode="HTML",
        )

    # Notify bot admin about confirmed payment
    for admin_id in settings.admin_ids:
        try:
            await callback.bot.send_message(
                chat_id=admin_id,
                text=(
                    f"✅ To'lov tasdiqlandi\n\n"
                    f"Buyurtma: #{order_id}\n"
                    f"Kanal: @{order.channel.channel_username}\n"
                    f"Summa: {format_price(order.price)} so'm\n"
                    f"Kanal egasi tasdiqladi: {callback.from_user.full_name}"
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    await callback.answer()


@router.callback_query(F.data.startswith("admin_pay:reject:"))
async def reject_payment(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    order_id = int(callback.data.split(":")[2])
    order = await order_repo.get_order(session, order_id)

    await callback.message.edit_caption(
        caption=f"❌ Buyurtma #{order_id} to'lovi rad etildi.",
    )

    # Notify advertiser
    if order:
        try:
            adv_lang = order.advertiser.language or "uz"
            await callback.bot.send_message(
                chat_id=order.advertiser_telegram_id,
                text=get_text("payment.rejected", adv_lang),
                parse_mode="HTML",
            )
        except Exception:
            pass

    await callback.answer()


# ─── All orders + Income tracking (Admin) ───
@router.message(F.text.in_(menu_match("admin.all_orders")))
async def all_orders(message: Message, session: AsyncSession, lang: str = "uz", **kwargs):
    if not is_admin(message.from_user.id):
        await message.answer(get_text("access_denied", lang), parse_mode="HTML")
        return

    from datetime import datetime
    from bot.database.repositories import commission_repo

    now = datetime.utcnow()
    orders_data = await order_repo.count_orders(session)
    summaries = await commission_repo.get_owner_income_summary(session, now.year, now.month)

    text = (
        f"📋 <b>Buyurtmalar statistikasi:</b>\n\n"
        f"Jami: <b>{orders_data['total']}</b>\n"
        f"Bugun: <b>{orders_data['today']}</b>\n"
        f"Bu hafta: <b>{orders_data['week']}</b>\n\n"
    )

    if summaries:
        text += f"💰 <b>{now.strftime('%B %Y')} daromadlar:</b>\n\n"
        for s in summaries:
            owner = s["owner"]
            paid_status = "✅" if s["is_paid"] else "❌"
            text += (
                f"👤 {owner.full_name or '—'} (@{owner.username or '—'})\n"
                f"   Daromad: {format_price(s['income'])} so'm\n"
                f"   Komissiya (5%): {format_price(s['commission'])} so'm {paid_status}\n\n"
            )

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Komissiyalar", callback_data="admin:commissions")
    builder.button(text="⚠️ Qarzdorlarni bloklash", callback_data="admin:block_overdue")
    builder.adjust(1)

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


# ─── Commission management (Admin) ───
@router.callback_query(F.data == "admin:commissions")
async def show_commissions(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("access_denied", lang), show_alert=True)
        return

    from bot.database.repositories import commission_repo

    unpaid = await commission_repo.get_unpaid_commissions(session)

    if not unpaid:
        await callback.message.edit_text(
            "✅ Hozircha to'lanmagan komissiyalar yo'q.", parse_mode="HTML"
        )
        await callback.answer()
        return

    text = "💰 <b>To'lanmagan komissiyalar:</b>\n\n"
    for c in unpaid:
        text += (
            f"👤 {c.owner.full_name or '—'}\n"
            f"   {c.year}/{c.month:02d} — {format_price(c.commission_amount)} so'm\n"
            f"   Muddat: {c.due_date.strftime('%d.%m.%Y') if c.due_date else '—'}\n\n"
        )

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:block_overdue")
async def block_overdue(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("access_denied", lang), show_alert=True)
        return

    from bot.database.repositories import commission_repo

    count = await commission_repo.deactivate_overdue_channels(session)

    if count > 0:
        await callback.message.answer(
            f"🔴 {count} ta kanal bloklandi (komissiya to'lanmagan).",
            parse_mode="HTML",
        )
    else:
        await callback.message.answer(
            "✅ Qarzdor kanal egalar topilmadi.", parse_mode="HTML"
        )
    await callback.answer()


# ─── Promo codes (Admin) ───
@router.message(F.text == "🏷 Promokodlar")
async def show_promos(message: Message, session: AsyncSession, lang: str = "uz", **kwargs):
    if not is_admin(message.from_user.id):
        await message.answer(get_text("access_denied", lang), parse_mode="HTML")
        return

    from bot.database.repositories import promo_repo

    promos = await promo_repo.get_all_promos(session)

    if not promos:
        text = "🏷 <b>Promokodlar yo'q.</b>\n\nYangi promokod yaratish uchun tugmani bosing."
    else:
        text = "🏷 <b>Promokodlar:</b>\n\n"
        for p in promos:
            status = "✅" if p.is_active else "❌"
            desc = f"{p.discount_percent}%" if p.discount_percent > 0 else f"{format_price(p.discount_amount)} so'm"
            uses = f"{p.used_count}/{p.max_uses}" if p.max_uses > 0 else f"{p.used_count}/♾"
            text += (
                f"{status} <code>{p.code}</code> — {desc}\n"
                f"   Ishlatilgan: {uses}\n\n"
            )

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Yangi promokod", callback_data="admin:create_promo")
    builder.adjust(1)

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
