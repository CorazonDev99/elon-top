"""
Order handler — FSM flow for creating an ad order.
Flow: select format → send ad content → select date → preview → confirm
"""

from datetime import datetime, date, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.channels import ad_formats_kb
from bot.keyboards.order import order_confirm_kb, payment_kb
from bot.keyboards.main_menu import main_menu_kb, cancel_kb
from bot.states.order_states import OrderStates, PaymentStates
from bot.database.repositories import channel_repo, order_repo
from bot.utils.formatting import format_price
from bot.config import settings

router = Router()


# ─── Step 1: Start order → select format ───
@router.callback_query(F.data.startswith("order:start:"))
async def start_order(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    channel_id = int(callback.data.split(":")[2])
    channel = await channel_repo.get_channel_full(session, channel_id)

    if not channel or not channel.pricing:
        await callback.answer("No pricing available", show_alert=True)
        return

    await state.set_state(OrderStates.select_format)
    await state.update_data(channel_id=channel_id)

    await callback.message.edit_text(
        get_text("order.select_format", lang, formats=""),
        reply_markup=ad_formats_kb(channel.pricing, channel_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Step 2: Format selected → ask for ad content ───
@router.callback_query(F.data.startswith("order:format:"))
async def select_format(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    parts = callback.data.split(":")
    channel_id = int(parts[2])
    format_id = int(parts[3])

    # Get price for this format
    pricing = await order_repo.get_channel_pricing(session, channel_id, format_id)
    if not pricing:
        await callback.answer("Price not found", show_alert=True)
        return

    ad_format = await channel_repo.get_ad_format(session, format_id)

    await state.update_data(
        channel_id=channel_id,
        format_id=format_id,
        price=pricing.price,
        format_name_uz=ad_format.name_uz,
        format_name_ru=ad_format.name_ru,
    )
    await state.set_state(OrderStates.send_ad_content)

    await callback.message.edit_text(
        get_text("order.send_text", lang),
        parse_mode="HTML",
    )
    await callback.message.answer(
        get_text("order.send_text", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Step 3: Receive ad content → ask for date ───
@router.message(OrderStates.send_ad_content)
async def receive_ad_content(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    ad_text = None
    ad_media_file_id = None
    ad_media_type = None

    if message.photo:
        ad_media_file_id = message.photo[-1].file_id
        ad_media_type = "photo"
        ad_text = message.caption
    elif message.video:
        ad_media_file_id = message.video.file_id
        ad_media_type = "video"
        ad_text = message.caption
    elif message.document:
        ad_media_file_id = message.document.file_id
        ad_media_type = "document"
        ad_text = message.caption
    elif message.text:
        ad_text = message.text
    else:
        await message.answer(get_text("order.send_text", lang), parse_mode="HTML")
        return

    await state.update_data(
        ad_text=ad_text,
        ad_media_file_id=ad_media_file_id,
        ad_media_type=ad_media_type,
    )
    await state.set_state(OrderStates.select_date)

    await message.answer(
        get_text("order.send_date", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )


# ─── Step 4: Receive date → show preview ───
@router.message(OrderStates.select_date)
async def receive_date(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    text = message.text.strip().lower()

    today_words = ["bugun", "сегодня", "today"]
    tomorrow_words = ["ertaga", "завтра", "tomorrow"]

    if text in today_words:
        desired = date.today()
    elif text in tomorrow_words:
        desired = date.today() + timedelta(days=1)
    else:
        try:
            desired = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            await message.answer(
                get_text("order.invalid_date", lang), parse_mode="HTML"
            )
            return

    data = await state.get_data()
    channel = await channel_repo.get_channel_full(session, data["channel_id"])
    format_name = data["format_name_uz"] if lang == "uz" else data["format_name_ru"]

    await state.update_data(desired_date=desired.isoformat())
    await state.set_state(OrderStates.preview)

    await message.answer(
        get_text(
            "order.preview",
            lang,
            channel=f"{channel.channel_title} (@{channel.channel_username})",
            format=format_name,
            price=format_price(data["price"]),
            date=desired.strftime("%d.%m.%Y"),
        ),
        reply_markup=order_confirm_kb(lang),
        parse_mode="HTML",
    )


# ─── Step 5: Confirm order ───
@router.callback_query(F.data == "order:confirm", OrderStates.preview)
async def confirm_order(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    data = await state.get_data()
    desired = date.fromisoformat(data["desired_date"]) if data.get("desired_date") else None

    order = await order_repo.create_order(
        session=session,
        advertiser_telegram_id=callback.from_user.id,
        channel_id=data["channel_id"],
        ad_format_id=data["format_id"],
        price=data["price"],
        ad_text=data.get("ad_text"),
        ad_media_file_id=data.get("ad_media_file_id"),
        ad_media_type=data.get("ad_media_type"),
        desired_date=desired,
    )

    await state.clear()

    # Notify advertiser
    await callback.message.edit_text(
        get_text("order.created", lang, id=order.id),
        parse_mode="HTML",
    )
    await callback.message.answer(
        get_text("menu.main", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )

    # Notify channel owner
    channel = await channel_repo.get_channel_full(session, data["channel_id"])
    if channel and channel.owner:
        format_name = data["format_name_uz"]  # default to uz for owner
        from bot.keyboards.order import order_action_kb

        try:
            # Send ad content to owner
            notify_text = get_text(
                "notify.new_order",
                channel.owner.language or "uz",
                channel=channel.channel_title,
                format=format_name,
                price=format_price(data["price"]),
                date=desired.strftime("%d.%m.%Y") if desired else "—",
                advertiser=callback.from_user.full_name,
            )

            await callback.bot.send_message(
                chat_id=channel.owner.telegram_id,
                text=notify_text,
                reply_markup=order_action_kb(order.id, channel.owner.language or "uz", for_owner=True),
                parse_mode="HTML",
            )

            # Forward the ad content
            if data.get("ad_media_file_id"):
                media_type = data.get("ad_media_type", "photo")
                if media_type == "photo":
                    await callback.bot.send_photo(
                        chat_id=channel.owner.telegram_id,
                        photo=data["ad_media_file_id"],
                        caption=data.get("ad_text") or "",
                    )
                elif media_type == "video":
                    await callback.bot.send_video(
                        chat_id=channel.owner.telegram_id,
                        video=data["ad_media_file_id"],
                        caption=data.get("ad_text") or "",
                    )
            elif data.get("ad_text"):
                await callback.bot.send_message(
                    chat_id=channel.owner.telegram_id,
                    text=f"📝 Reklama matni:\n\n{data['ad_text']}",
                )
        except Exception:
            pass  # Owner might have blocked the bot

    await callback.answer()


# ─── Cancel order ───
@router.callback_query(F.data == "order:cancel")
async def cancel_order(
    callback: CallbackQuery, state: FSMContext, lang: str = "uz", **kwargs
):
    await state.clear()
    await callback.message.edit_text(
        get_text("order.cancelled", lang), parse_mode="HTML"
    )
    await callback.message.answer(
        get_text("menu.main", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Payment flow ───
@router.callback_query(F.data.startswith("payment:send:"))
async def start_payment(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    order_id = int(callback.data.split(":")[2])
    order = await order_repo.get_order(session, order_id)

    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    await state.set_state(PaymentStates.waiting_screenshot)
    await state.update_data(payment_order_id=order_id)

    await callback.message.edit_text(
        get_text(
            "payment.info",
            lang,
            card=settings.admin_card_number,
            amount=format_price(order.price),
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(PaymentStates.waiting_screenshot, F.photo)
async def receive_payment_screenshot(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    data = await state.get_data()
    order_id = data.get("payment_order_id")
    file_id = message.photo[-1].file_id

    await order_repo.save_payment_screenshot(session, order_id, file_id)
    await state.clear()

    await message.answer(
        get_text("payment.screenshot_received", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )

    # Notify admins
    from bot.keyboards.order import admin_payment_kb

    order = await order_repo.get_order(session, order_id)
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=(
                    f"💳 To'lov screenshot\n\n"
                    f"Buyurtma: #{order_id}\n"
                    f"Summa: {format_price(order.price)} so'm\n"
                    f"Buyurtmachi: {message.from_user.full_name}"
                ),
                reply_markup=admin_payment_kb(order_id),
            )
        except Exception:
            pass
