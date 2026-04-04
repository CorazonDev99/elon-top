"""
Admin handler — statistics, channel moderation, broadcast, payment confirmations.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb, cancel_kb
from bot.keyboards.admin import admin_menu_kb, moderate_channel_kb, confirm_broadcast_kb
from bot.states.admin_states import AdminStates
from bot.database.repositories import channel_repo, order_repo, user_repo
from bot.utils.formatting import format_price
from bot.config import settings

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


# ─── Stats ───
@router.message(F.text.in_(["📊 Statistika", "📊 Статистика"]))
async def show_stats(message: Message, session: AsyncSession, lang: str = "uz", **kwargs):
    if not is_admin(message.from_user.id):
        await message.answer(get_text("access_denied", lang), parse_mode="HTML")
        return

    users_count = await user_repo.count_users(session)
    channels_data = await channel_repo.count_channels(session)
    orders_data = await order_repo.count_orders(session)

    await message.answer(
        get_text(
            "admin.stats_text",
            lang,
            users=users_count,
            channels=channels_data["total"],
            verified=channels_data["verified"],
            pending=channels_data["pending"],
            orders=orders_data["total"],
            today_orders=orders_data["today"],
            week_orders=orders_data["week"],
        ),
        reply_markup=admin_menu_kb(lang),
        parse_mode="HTML",
    )


# ─── Moderation ───
@router.message(F.text.in_(["✅ Moderatsiya", "✅ Модерация"]))
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
@router.message(F.text.in_(["📢 Xabar yuborish", "📢 Рассылка"]))
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
    users = await user_repo.get_all_users(session)
    await state.update_data(broadcast_message=message.text, user_count=len(users))
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
    text = data["broadcast_message"]
    users = await user_repo.get_all_users(session)

    await state.clear()
    await callback.message.edit_text("⏳ Yuborilmoqda...", parse_mode="HTML")

    sent = 0
    for user in users:
        try:
            await callback.bot.send_message(
                chat_id=user.telegram_id,
                text=text,
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


# ─── Payment confirmations ───
@router.callback_query(F.data.startswith("admin_pay:confirm:"))
async def confirm_payment(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("access_denied", lang), show_alert=True)
        return

    order_id = int(callback.data.split(":")[2])
    order = await order_repo.get_order(session, order_id)
    await order_repo.update_order_status(session, order_id, "paid")

    await callback.message.edit_caption(
        caption=f"✅ Buyurtma #{order_id} to'lovi tasdiqlandi.",
    )

    # Notify advertiser
    if order:
        try:
            adv_lang = order.advertiser.language or "uz"
            await callback.bot.send_message(
                chat_id=order.advertiser_telegram_id,
                text=get_text("payment.confirmed", adv_lang),
                parse_mode="HTML",
            )
        except Exception:
            pass

        # Notify channel owner to publish
        try:
            from bot.keyboards.order import owner_published_kb

            owner_lang = order.channel.owner.language or "uz" if order.channel.owner else "uz"
            await callback.bot.send_message(
                chat_id=order.channel.owner.telegram_id,
                text=(
                    f"💰 Buyurtma #{order_id} uchun to'lov tasdiqlandi!\n\n"
                    f"Iltimos, reklamani chop eting va tugmani bosing."
                ),
                reply_markup=owner_published_kb(order_id, owner_lang),
                parse_mode="HTML",
            )
        except Exception:
            pass

    await callback.answer()


@router.callback_query(F.data.startswith("admin_pay:reject:"))
async def reject_payment(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("access_denied", lang), show_alert=True)
        return

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


# ─── All orders ───
@router.message(F.text.in_(["📋 Barcha buyurtmalar", "📋 Все заказы"]))
async def all_orders(message: Message, session: AsyncSession, lang: str = "uz", **kwargs):
    if not is_admin(message.from_user.id):
        await message.answer(get_text("access_denied", lang), parse_mode="HTML")
        return

    orders_data = await order_repo.count_orders(session)
    text = (
        f"📋 <b>Buyurtmalar statistikasi:</b>\n\n"
        f"Jami: <b>{orders_data['total']}</b>\n"
        f"Bugun: <b>{orders_data['today']}</b>\n"
        f"Bu hafta: <b>{orders_data['week']}</b>"
    )
    await message.answer(text, parse_mode="HTML")
