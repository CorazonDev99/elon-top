"""
My orders handler — shows advertiser's orders with details and cancel option.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.order import order_action_kb, payment_kb
from bot.database.repositories import order_repo
from bot.utils.formatting import format_price

router = Router()


async def show_my_orders(message: Message, lang: str = "uz", **kwargs):
    session: AsyncSession = kwargs.get("session")
    if not session:
        return

    orders = await order_repo.get_orders_by_advertiser(session, message.from_user.id)

    if not orders:
        await message.answer(
            get_text("my_orders.empty", lang), parse_mode="HTML"
        )
        return

    # Show advertiser stats
    stats = await order_repo.get_advertiser_stats(session, message.from_user.id)
    text = get_text(
        "my_orders.stats", lang,
        total_orders=stats["total_orders"],
        completed=stats["completed"],
        total_spent=format_price(stats["total_spent"]),
    ) + "\n\n"

    text += get_text("my_orders.title", lang) + "\n\n"
    for order in orders[:20]:
        fmt_name = order.ad_format.name_uz if lang == "uz" else order.ad_format.name_ru
        status = get_text(f"status.{order.status}", lang)
        text += get_text(
            "my_orders.item",
            lang,
            id=order.id,
            channel=order.channel.channel_title,
            format=fmt_name,
            price=format_price(order.price),
            status=status,
        )

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    for order in orders[:10]:
        builder.button(
            text=f"📋 #{order.id}",
            callback_data=f"my_order:detail:{order.id}",
        )
    builder.adjust(5)

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("my_order:detail:"))
async def order_detail(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    order_id = int(callback.data.split(":")[2])
    order = await order_repo.get_order(session, order_id)

    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    fmt_name = order.ad_format.name_uz if lang == "uz" else order.ad_format.name_ru
    status = get_text(f"status.{order.status}", lang)
    date_str = order.desired_date.strftime("%d.%m.%Y") if order.desired_date else "—"

    text = get_text(
        "my_orders.detail",
        lang,
        id=order.id,
        channel=f"{order.channel.channel_title} (@{order.channel.channel_username})",
        format=fmt_name,
        price=format_price(order.price),
        date=date_str,
        status=status,
        created=order.created_at.strftime("%d.%m.%Y %H:%M"),
    )

    # Show appropriate buttons based on status
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    if order.status == "pending":
        builder.button(
            text=get_text("my_orders.cancel_btn", lang),
            callback_data=f"my_order:cancel:{order.id}",
        )
    elif order.status == "accepted":
        builder.button(
            text="💳 " + get_text("order.confirm", lang),
            callback_data=f"payment:send:{order.id}",
        )
    elif order.status in ("published", "completed"):
        # Repeat order button
        builder.button(
            text=get_text("order.repeat", lang),
            callback_data=f"order:repeat:{order.id}",
        )
        # Rate button (if not rated yet)
        if not order.rating:
            builder.button(
                text="⭐ Baholash",
                callback_data=f"rate_prompt:{order.id}",
            )
        # Subscribe button
        builder.button(
            text="🔄 Obuna bo'lish" if lang == "uz" else "🔄 Подписаться",
            callback_data=f"sub:create:{order.id}",
        )
    builder.button(text=get_text("menu.back", lang), callback_data="my_order:back")
    builder.adjust(1)

    await callback.message.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("my_order:cancel:"))
async def cancel_my_order(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    order_id = int(callback.data.split(":")[2])
    order = await order_repo.get_order(session, order_id)

    if order and order.status == "pending":
        await order_repo.update_order_status(session, order_id, "cancelled")
        await callback.message.edit_text(
            get_text("order.cancelled", lang), parse_mode="HTML"
        )
    else:
        await callback.answer("Cannot cancel this order", show_alert=True)

    await callback.answer()


@router.callback_query(F.data == "my_order:back")
async def back_to_orders(callback: CallbackQuery, lang: str = "uz", **kwargs):
    # Re-show orders list
    session: AsyncSession = kwargs.get("session")
    orders = await order_repo.get_orders_by_advertiser(session, callback.from_user.id)

    if not orders:
        await callback.message.edit_text(
            get_text("my_orders.empty", lang), parse_mode="HTML"
        )
    else:
        text = get_text("my_orders.title", lang) + "\n\n"
        for order in orders[:20]:
            fmt_name = order.ad_format.name_uz if lang == "uz" else order.ad_format.name_ru
            status = get_text(f"status.{order.status}", lang)
            text += get_text(
                "my_orders.item",
                lang,
                id=order.id,
                channel=order.channel.channel_title,
                format=fmt_name,
                price=format_price(order.price),
                status=status,
            )

        from aiogram.utils.keyboard import InlineKeyboardBuilder

        builder = InlineKeyboardBuilder()
        for order in orders[:10]:
            builder.button(
                text=f"📋 #{order.id}",
                callback_data=f"my_order:detail:{order.id}",
            )
        builder.adjust(5)

        await callback.message.edit_text(
            text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )
    await callback.answer()
