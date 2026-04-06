"""
Channel owner handler — register channels, manage them, handle incoming orders.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb, cancel_kb
from bot.keyboards.regions import regions_kb, districts_kb
from bot.keyboards.order import order_action_kb, owner_published_kb
from bot.states.channel_reg import ChannelRegStates
from bot.states.order_states import RejectOrderStates
from bot.database.repositories import channel_repo, region_repo, order_repo, user_repo
from bot.utils.formatting import format_price
from bot.config import settings

router = Router()


# ─── Show my channels ───
async def show_my_channels(message: Message, lang: str = "uz", **kwargs):
    session: AsyncSession = kwargs.get("session")
    if not session:
        return

    channels = await channel_repo.get_channels_by_owner(session, message.from_user.id)

    if not channels:
        from aiogram.utils.keyboard import InlineKeyboardBuilder

        builder = InlineKeyboardBuilder()
        builder.button(
            text=get_text("owner.add_channel", lang),
            callback_data="owner:add_channel",
        )

        await message.answer(
            get_text("owner.no_channels", lang),
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
        return

    # Calculate income stats
    from datetime import datetime, timedelta
    from bot.database.repositories import commission_repo

    now = datetime.utcnow()
    monthly_income = await commission_repo.calculate_owner_monthly_income(
        session, message.from_user.id, now.year, now.month
    )
    commission_amount = int(monthly_income * 0.05)

    # Daily income (orders completed today)
    from sqlalchemy import select, func
    from bot.database.models import Order, Channel as ChannelModel

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    daily_result = await session.execute(
        select(func.coalesce(func.sum(Order.price), 0))
        .join(ChannelModel, Order.channel_id == ChannelModel.id)
        .where(
            ChannelModel.owner_telegram_id == message.from_user.id,
            Order.status.in_(["paid", "published", "completed"]),
            Order.updated_at >= today_start,
        )
    )
    daily_income = daily_result.scalar() or 0

    text = get_text("owner.panel", lang) + "\n\n"
    text += get_text(
        "owner.income_stats", lang,
        daily=format_price(daily_income),
        monthly=format_price(monthly_income),
        commission=format_price(commission_amount),
    ) + "\n\n"

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    for ch in channels:
        status = "✅" if ch.is_verified else "⏳"
        active = "🟢" if ch.is_active else "🔴"
        builder.button(
            text=f"{active}{status} {ch.channel_title}",
            callback_data=f"owner:channel:{ch.id}",
        )

    builder.button(
        text=get_text("owner.add_channel", lang),
        callback_data="owner:add_channel",
    )

    # Check for pending orders
    pending = await order_repo.get_pending_orders_for_owner(session, message.from_user.id)
    if pending:
        builder.button(
            text=f"📩 {get_text('owner.incoming_orders', lang).replace('<b>', '').replace('</b>', '')} ({len(pending)})",
            callback_data="owner:incoming_orders",
        )

    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


# ─── Add channel: Step 1 — enter username ───
@router.callback_query(F.data == "owner:add_channel")
async def add_channel_start(
    callback: CallbackQuery, state: FSMContext, lang: str = "uz", **kwargs
):
    await state.set_state(ChannelRegStates.enter_username)
    await callback.message.answer(
        get_text("owner.enter_username", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ChannelRegStates.enter_username)
async def enter_username(
    message: Message, session: AsyncSession, state: FSMContext, lang: str = "uz", **kwargs
):
    username = message.text.strip()
    if not username.startswith("@"):
        await message.answer(get_text("owner.invalid_username", lang), parse_mode="HTML")
        return

    username = username[1:]  # remove @

    # ─── Verify user is admin of the channel/group ───
    from aiogram import Bot
    bot: Bot = message.bot

    try:
        chat = await bot.get_chat(f"@{username}")
    except Exception:
        await message.answer(
            "⚠️ " + (
                "Kanal/guruh topilmadi. Username to'g'ri yozilganini tekshiring."
                if lang == "uz" else
                "Канал/группа не найден(а). Проверьте username."
            ),
            parse_mode="HTML",
        )
        return

    # Check that user is admin or creator
    try:
        member = await bot.get_chat_member(chat.id, message.from_user.id)
    except Exception:
        await message.answer(
            "⚠️ " + (
                "Bot bu kanal/guruhga kira olmadi. Botni admin qiling!"
                if lang == "uz" else
                "Бот не смог получить доступ. Добавьте бота админом!"
            ),
            parse_mode="HTML",
        )
        return

    if member.status not in ("creator", "administrator"):
        await message.answer(
            "🚫 " + (
                "Siz bu kanal/guruh admini emassiz! Faqat adminlar qo'sha oladi."
                if lang == "uz" else
                "Вы не админ этого канала/группы! Только админы могут добавлять."
            ),
            parse_mode="HTML",
        )
        return

    # ─── Check for duplicate ───
    existing = await channel_repo.get_channel_by_username(session, username)
    if existing:
        await message.answer(
            "⚠️ " + (
                f"@{username} allaqachon ro'yxatda mavjud!"
                if lang == "uz" else
                f"@{username} уже добавлен в систему!"
            ),
            parse_mode="HTML",
        )
        await state.clear()
        return

    # ─── Auto-fetch subscriber count ───
    try:
        member_count = await bot.get_chat_member_count(chat.id)
    except Exception:
        member_count = 0

    channel_title = chat.title or username
    avg_views = max(int(member_count * 0.3), 0)  # estimate ~30% of subs

    # Detect type: channel or group
    is_group = chat.type in ("group", "supergroup")
    type_label = ("guruh" if lang == "uz" else "группа") if is_group else ("kanal" if lang == "uz" else "канал")
    type_emoji = "👥" if is_group else "📺"

    await state.update_data(
        channel_username=username,
        channel_title=channel_title,
        subscribers_count=member_count,
        avg_views=avg_views,
        chat_id=chat.id,
        is_group=is_group,
    )

    info_text = (
        f"✅ {type_emoji} <b>{channel_title}</b> topildi!\n"
        f"📊 {member_count} ta a'zo | {type_label.capitalize()}\n\n"
        if lang == "uz" else
        f"✅ {type_emoji} <b>{channel_title}</b> найден(а)!\n"
        f"📊 {member_count} участн. | {type_label.capitalize()}\n\n"
    )

    # Check if user already has card number
    user = await user_repo.get_user(session, message.from_user.id)
    if user and user.card_number:
        await state.update_data(card_number=user.card_number)
        await state.set_state(ChannelRegStates.select_region)
        regions = await region_repo.get_all_regions(session)
        await message.answer(
            info_text + get_text("owner.select_region", lang),
            reply_markup=regions_kb(regions, lang),
            parse_mode="HTML",
        )
    else:
        await state.set_state(ChannelRegStates.enter_card_number)
        await message.answer(
            info_text + get_text("owner.enter_card", lang),
            reply_markup=cancel_kb(lang),
            parse_mode="HTML",
        )


# ─── Step 2: Enter card number ───
@router.message(ChannelRegStates.enter_card_number)
async def enter_card_number(
    message: Message, session: AsyncSession, state: FSMContext, lang: str = "uz", **kwargs
):
    card = message.text.strip().replace(" ", "")
    if not card.isdigit() or len(card) != 16:
        await message.answer(get_text("owner.invalid_card", lang), parse_mode="HTML")
        return

    # Save card to user profile
    await user_repo.update_card_number(session, message.from_user.id, card)
    await state.update_data(card_number=card)
    await state.set_state(ChannelRegStates.select_region)

    regions = await region_repo.get_all_regions(session)
    await message.answer(
        get_text("owner.select_region", lang),
        reply_markup=regions_kb(regions, lang),
        parse_mode="HTML",
    )


# ─── Step 3: Select region ───
@router.callback_query(F.data.startswith("region:"), ChannelRegStates.select_region)
async def reg_select_region(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    region_id = int(callback.data.split(":")[1])
    await state.update_data(region_id=region_id)

    districts = await region_repo.get_districts_by_region(session, region_id)
    await state.set_state(ChannelRegStates.select_district)

    await callback.message.edit_text(
        get_text("owner.select_district", lang),
        reply_markup=districts_kb(districts, region_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Step 4: Select district ───
@router.callback_query(F.data.startswith("district:"), ChannelRegStates.select_district)
async def reg_select_district(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    district_id = int(callback.data.split(":")[1])
    await state.update_data(district_id=district_id)

    # Show categories
    categories = await channel_repo.get_categories(session)
    from bot.utils.pagination import paginate_buttons

    items = [
        (f"{c.emoji} {c.name_uz if lang == 'uz' else c.name_ru}", f"cat:{c.id}")
        for c in categories
    ]
    kb = paginate_buttons(items, columns=2, per_page=10 )

    await state.set_state(ChannelRegStates.select_category)
    await callback.message.edit_text(
        get_text("owner.select_category", lang),
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Step 5: Select category → skip to description (subs & views auto) ───
@router.callback_query(F.data.startswith("cat:"), ChannelRegStates.select_category)
async def reg_select_category(
    callback: CallbackQuery, state: FSMContext, lang: str = "uz", **kwargs
):
    category_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=category_id)
    await state.set_state(ChannelRegStates.enter_description)

    await callback.message.edit_text(
        get_text("owner.enter_description", lang), parse_mode="HTML"
    )
    await callback.answer()


# ─── Step 6: Enter subscribers count ───
@router.message(ChannelRegStates.enter_subscribers)
async def enter_subscribers(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    try:
        count = int(message.text.strip().replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer(get_text("owner.invalid_number", lang), parse_mode="HTML")
        return

    await state.update_data(subscribers_count=count)
    await state.set_state(ChannelRegStates.enter_views)
    await message.answer(
        get_text("owner.enter_views", lang), parse_mode="HTML"
    )


# ─── Step 7: Enter avg views ───
@router.message(ChannelRegStates.enter_views)
async def enter_views(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    try:
        count = int(message.text.strip().replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer(get_text("owner.invalid_number", lang), parse_mode="HTML")
        return

    await state.update_data(avg_views=count)
    await state.set_state(ChannelRegStates.enter_description)
    await message.answer(
        get_text("owner.enter_description", lang), parse_mode="HTML"
    )


# ─── Step 8: Enter description ───
@router.message(ChannelRegStates.enter_description)
async def enter_description(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    await state.update_data(description=message.text.strip())

    # Start price setting for each format
    formats = await channel_repo.get_ad_formats(session)
    await state.update_data(
        ad_formats=[{"id": f.id, "name_uz": f.name_uz, "name_ru": f.name_ru} for f in formats],
        current_format_index=0,
        prices={},
    )
    await state.set_state(ChannelRegStates.set_price)

    fmt = formats[0]
    fmt_name = fmt.name_uz if lang == "uz" else fmt.name_ru
    await message.answer(
        get_text("owner.set_prices", lang, format=fmt_name),
        parse_mode="HTML",
    )


# ─── Step 9: Set prices (loops through formats) ───
@router.message(ChannelRegStates.set_price)
async def set_price(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    try:
        price = int(message.text.strip().replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer(get_text("owner.invalid_number", lang), parse_mode="HTML")
        return

    data = await state.get_data()
    formats = data["ad_formats"]
    idx = data["current_format_index"]
    prices = data["prices"]

    # Save this price
    fmt = formats[idx]
    prices[fmt["id"]] = price

    # Move to next format or finish
    next_idx = idx + 1
    if next_idx < len(formats):
        await state.update_data(current_format_index=next_idx, prices=prices)
        next_fmt = formats[next_idx]
        fmt_name = next_fmt["name_uz"] if lang == "uz" else next_fmt["name_ru"]
        await message.answer(
            get_text("owner.set_prices", lang, format=fmt_name),
            parse_mode="HTML",
        )
    else:
        # All prices set — create channel
        await state.update_data(prices=prices)
        data = await state.get_data()

        is_group = data.get("is_group", False)
        type_word_uz = "Guruh" if is_group else "Kanal"
        type_word_ru = "Группа" if is_group else "Канал"
        type_emoji = "👥" if is_group else "📺"

        channel = await channel_repo.create_channel(
            session=session,
            owner_telegram_id=message.from_user.id,
            channel_username=data["channel_username"],
            channel_title=data["channel_title"],
            district_id=data["district_id"],
            category_id=data["category_id"],
            subscribers_count=data["subscribers_count"],
            avg_views=data["avg_views"],
            description=data["description"],
            prices={int(k): v for k, v in data["prices"].items()},
            is_group=data.get("is_group", False),
        )

        await state.clear()

        added_text = (
            f"✅ <b>{type_word_uz} qo'shildi!</b>\n\n"
            f"{type_emoji} {channel.channel_title} (@{channel.channel_username})\n\n"
            f"Moderatsiyaga yuborildi ⏳"
            if lang == "uz" else
            f"✅ <b>{type_word_ru} добавлен(а)!</b>\n\n"
            f"{type_emoji} {channel.channel_title} (@{channel.channel_username})\n\n"
            f"Отправлено на модерацию ⏳"
        )

        await message.answer(
            added_text,
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )

        # Notify admins about new channel/group for moderation
        from bot.config import settings
        from bot.keyboards.admin import moderate_channel_kb

        type_admin = "guruh" if is_group else "kanal"
        for admin_id in settings.admin_ids:
            try:
                await message.bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"🆕 Yangi {type_admin} moderatsiya uchun:\n\n"
                        f"{type_emoji} @{channel.channel_username}\n"
                        f"👥 {channel.subscribers_count} a'zo\n"
                        f"👤 Egasi: {message.from_user.full_name}"
                    ),
                    reply_markup=moderate_channel_kb(channel.id),
                    parse_mode="HTML",
                )
            except Exception:
                pass


# ─── Manage existing channel ───
@router.callback_query(F.data.startswith("owner:channel:"))
async def manage_channel(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    channel_id = int(callback.data.split(":")[2])
    channel = await channel_repo.get_channel_full(session, channel_id)

    if not channel:
        await callback.answer("Channel not found", show_alert=True)
        return

    status = get_text("channel.verified" if channel.is_verified else "channel.not_verified", lang)
    active_str = "🟢 Active" if channel.is_active else "🔴 Inactive"

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_text("owner.edit_prices", lang),
        callback_data=f"owner:edit_prices:{channel.id}",
    )
    builder.button(
        text=get_text("owner.toggle_active", lang),
        callback_data=f"owner:toggle:{channel.id}",
    )
    builder.button(
        text=get_text("owner.delete_channel", lang),
        callback_data=f"owner:delete:{channel.id}",
    )
    builder.button(
        text=get_text("menu.back", lang),
        callback_data="owner:back_to_list",
    )
    builder.adjust(1)

    await callback.message.edit_text(
        get_text(
            "owner.manage_channel",
            lang,
            title=channel.channel_title,
            username=channel.channel_username,
            subscribers=channel.subscribers_count,
            views=channel.avg_views,
            status=f"{status} | {active_str}",
        ),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("owner:toggle:"))
async def toggle_channel(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    channel_id = int(callback.data.split(":")[2])
    is_active = await channel_repo.toggle_channel_active(session, channel_id)
    msg = get_text("owner.channel_activated" if is_active else "owner.channel_deactivated", lang)
    await callback.answer(msg, show_alert=True)
    # Refresh the manage view
    await manage_channel(callback, session, lang, **kwargs)


@router.callback_query(F.data.startswith("owner:delete:"))
async def delete_channel(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    channel_id = int(callback.data.split(":")[2])
    await channel_repo.delete_channel(session, channel_id)
    await callback.message.edit_text(
        get_text("owner.channel_deleted", lang), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "owner:back_to_list")
async def back_to_channel_list(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    channels = await channel_repo.get_channels_by_owner(session, callback.from_user.id)
    text = get_text("owner.panel", lang) + "\n\n"
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    for ch in channels:
        status = "✅" if ch.is_verified else "⏳"
        active = "🟢" if ch.is_active else "🔴"
        builder.button(
            text=f"{active}{status} {ch.channel_title}",
            callback_data=f"owner:channel:{ch.id}",
        )
    builder.button(
        text=get_text("owner.add_channel", lang),
        callback_data="owner:add_channel",
    )
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ─── Incoming orders for channel owner ───
@router.callback_query(F.data == "owner:incoming_orders")
async def incoming_orders(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    orders = await order_repo.get_pending_orders_for_owner(session, callback.from_user.id)

    if not orders:
        await callback.message.edit_text(
            get_text("owner.no_orders", lang), parse_mode="HTML"
        )
        await callback.answer()
        return

    for order in orders:
        fmt_name = order.ad_format.name_uz if lang == "uz" else order.ad_format.name_ru
        text = get_text(
            "notify.new_order",
            lang,
            channel=order.channel.channel_title,
            format=fmt_name,
            price=format_price(order.price),
            date=order.desired_date.strftime("%d.%m.%Y") if order.desired_date else "—",
            advertiser=order.advertiser.full_name or "—",
        )
        await callback.message.answer(
            text,
            reply_markup=order_action_kb(order.id, lang, for_owner=True),
            parse_mode="HTML",
        )

    await callback.answer()


# ─── Accept / Reject orders ───
@router.callback_query(F.data.startswith("owner_order:accept:"))
async def accept_order(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    order_id = int(callback.data.split(":")[2])
    order = await order_repo.get_order(session, order_id)

    if not order or order.status != "pending":
        await callback.answer("Order unavailable", show_alert=True)
        return

    await order_repo.update_order_status(session, order_id, "accepted")

    await callback.message.edit_text(
        get_text("owner.order_accepted", lang, id=order_id),
        parse_mode="HTML",
    )

    # Notify advertiser
    try:
        adv_lang = order.advertiser.language or "uz"
        fmt_name = order.ad_format.name_uz if adv_lang == "uz" else order.ad_format.name_ru
        from bot.keyboards.order import payment_kb

        await callback.bot.send_message(
            chat_id=order.advertiser_telegram_id,
            text=get_text(
                "notify.order_accepted",
                adv_lang,
                channel=order.channel.channel_title,
                format=fmt_name,
                price=format_price(order.price),
            ),
            reply_markup=payment_kb(order.id, adv_lang),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await callback.answer()


@router.callback_query(F.data.startswith("owner_order:reject:"))
async def reject_order_start(
    callback: CallbackQuery,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    order_id = int(callback.data.split(":")[2])
    await state.set_state(RejectOrderStates.enter_reason)
    await state.update_data(reject_order_id=order_id)

    await callback.message.answer(
        get_text("owner.enter_reject_reason", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(RejectOrderStates.enter_reason)
async def reject_order_reason(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    data = await state.get_data()
    order_id = data["reject_order_id"]
    reason = message.text.strip()

    order = await order_repo.get_order(session, order_id)
    await order_repo.update_order_status(session, order_id, "rejected", reason)
    await state.clear()

    await message.answer(
        get_text("owner.order_rejected", lang, id=order_id),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )

    # Notify advertiser
    if order:
        try:
            adv_lang = order.advertiser.language or "uz"
            await message.bot.send_message(
                chat_id=order.advertiser_telegram_id,
                text=get_text(
                    "notify.order_rejected",
                    adv_lang,
                    channel=order.channel.channel_title,
                    reason=reason,
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass


@router.callback_query(F.data.startswith("owner_order:published:"))
async def mark_published(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    order_id = int(callback.data.split(":")[2])
    await order_repo.update_order_status(session, order_id, "published")

    await callback.message.edit_text(
        f"✅ Buyurtma #{order_id} chop etildi deb belgilandi.",
        parse_mode="HTML",
    )
    await callback.answer()
