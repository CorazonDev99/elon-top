"""
Rating, post report, and promo code handlers.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb
from bot.database.repositories import order_repo, channel_repo
from bot.database.repositories import promo_repo
from bot.utils.formatting import format_price
from bot.config import settings

router = Router()


class ReportStates(StatesGroup):
    waiting_views = State()
    waiting_reach = State()


class PromoStates(StatesGroup):
    waiting_code = State()
    waiting_percent = State()
    waiting_amount = State()
    waiting_max_uses = State()


# ─── Rating (after order published) ───
def rating_kb(order_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        stars = "⭐" * i
        builder.button(text=stars, callback_data=f"rate:{order_id}:{i}")
    builder.adjust(5)
    return builder


@router.callback_query(F.data.startswith("rate:"))
async def rate_channel(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    parts = callback.data.split(":")
    order_id = int(parts[1])
    rating = int(parts[2])

    await order_repo.rate_order(session, order_id, rating)

    stars = "⭐" * rating
    await callback.message.edit_text(
        f"✅ Baholandi: {stars}\n\nRahmat!",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rate_prompt:"))
async def rate_prompt(
    callback: CallbackQuery, session: AsyncSession, lang: str = "uz", **kwargs
):
    order_id = int(callback.data.split(":")[1])
    order = await order_repo.get_order(session, order_id)

    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    channel_name = order.channel.channel_title if order.channel else "—"
    builder = rating_kb(order_id)

    await callback.message.answer(
        get_text("rating.request", lang, channel=channel_name),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Post report (owner submits views/reach after publishing) ───
@router.callback_query(F.data.startswith("report:start:"))
async def start_report(
    callback: CallbackQuery, state: FSMContext, lang: str = "uz", **kwargs
):
    order_id = int(callback.data.split(":")[2])
    await state.set_state(ReportStates.waiting_views)
    await state.update_data(report_order_id=order_id)

    await callback.message.answer(
        get_text("report.enter_views", lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ReportStates.waiting_views)
async def report_views(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    try:
        views = int(message.text.strip().replace(" ", ""))
    except ValueError:
        await message.answer("⚠️ Raqam kiriting.", parse_mode="HTML")
        return

    await state.update_data(report_views=views)
    await state.set_state(ReportStates.waiting_reach)
    await message.answer(
        get_text("report.enter_reach", lang),
        parse_mode="HTML",
    )


@router.message(ReportStates.waiting_reach)
async def report_reach(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str = "uz",
    **kwargs,
):
    try:
        reach = int(message.text.strip().replace(" ", ""))
    except ValueError:
        await message.answer("⚠️ Raqam kiriting.", parse_mode="HTML")
        return

    data = await state.get_data()
    order_id = data["report_order_id"]
    views = data["report_views"]

    await order_repo.save_post_report(session, order_id, views, reach)
    await state.clear()

    await message.answer(
        get_text("report.saved", lang, views=views, reach=reach),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )

    # Send rating request to advertiser
    order = await order_repo.get_order(session, order_id)
    if order:
        try:
            adv_lang = order.advertiser.language or "uz"
            builder = rating_kb(order_id)
            await message.bot.send_message(
                chat_id=order.advertiser_telegram_id,
                text=get_text(
                    "rating.request", adv_lang,
                    channel=order.channel.channel_title,
                ),
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
        except Exception:
            pass


# ─── Repeat order ───
@router.callback_query(F.data.startswith("order:repeat:"))
async def repeat_order(
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

    # Start new order with same channel
    channel = await channel_repo.get_channel_full(session, order.channel_id)
    if not channel or not channel.pricing:
        await callback.answer("Channel not available", show_alert=True)
        return

    from bot.states.order_states import OrderStates
    from bot.keyboards.channels import ad_formats_kb

    await state.set_state(OrderStates.select_format)
    await state.update_data(channel_id=order.channel_id)

    await callback.message.answer(
        get_text("order.select_format", lang, formats=""),
        reply_markup=ad_formats_kb(channel.pricing, channel.id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Promo code management (Admin) ───
@router.callback_query(F.data == "admin:create_promo")
async def admin_create_promo(
    callback: CallbackQuery, state: FSMContext, lang: str = "uz", **kwargs
):
    if callback.from_user.id not in settings.admin_ids:
        await callback.answer("🚫", show_alert=True)
        return

    await state.set_state(PromoStates.waiting_code)
    await callback.message.answer(
        "📝 Promokod nomini kiriting (masalan: SALE10):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(PromoStates.waiting_code)
async def promo_code_name(message: Message, state: FSMContext, **kwargs):
    code = message.text.strip().upper()
    await state.update_data(promo_code=code)
    await state.set_state(PromoStates.waiting_percent)
    await message.answer(
        "📊 Chegirma foizini kiriting (masalan: 10).\n0 kiriting agar summa bo'yicha bo'lsa:",
        parse_mode="HTML",
    )


@router.message(PromoStates.waiting_percent)
async def promo_percent(message: Message, state: FSMContext, **kwargs):
    try:
        percent = int(message.text.strip())
    except ValueError:
        await message.answer("⚠️ Raqam kiriting.")
        return

    await state.update_data(promo_percent=percent)

    if percent > 0:
        await state.set_state(PromoStates.waiting_max_uses)
        await message.answer(
            "🔢 Maksimal foydalanish soni (0 = cheksiz):",
            parse_mode="HTML",
        )
    else:
        await state.set_state(PromoStates.waiting_amount)
        await message.answer(
            "💰 Chegirma summasini kiriting (so'mda):",
            parse_mode="HTML",
        )


@router.message(PromoStates.waiting_amount)
async def promo_amount(message: Message, state: FSMContext, **kwargs):
    try:
        amount = int(message.text.strip().replace(" ", ""))
    except ValueError:
        await message.answer("⚠️ Raqam kiriting.")
        return

    await state.update_data(promo_amount=amount)
    await state.set_state(PromoStates.waiting_max_uses)
    await message.answer(
        "🔢 Maksimal foydalanish soni (0 = cheksiz):",
        parse_mode="HTML",
    )


@router.message(PromoStates.waiting_max_uses)
async def promo_max_uses(
    message: Message, session: AsyncSession, state: FSMContext, **kwargs
):
    try:
        max_uses = int(message.text.strip())
    except ValueError:
        await message.answer("⚠️ Raqam kiriting.")
        return

    data = await state.get_data()
    promo = await promo_repo.create_promo(
        session,
        code=data["promo_code"],
        discount_percent=data.get("promo_percent", 0),
        discount_amount=data.get("promo_amount", 0),
        max_uses=max_uses,
    )
    await state.clear()

    desc = f"{promo.discount_percent}%" if promo.discount_percent > 0 else f"{format_price(promo.discount_amount)} so'm"
    await message.answer(
        f"✅ Promokod yaratildi!\n\n"
        f"📝 Kod: <code>{promo.code}</code>\n"
        f"💰 Chegirma: {desc}\n"
        f"🔢 Max: {promo.max_uses if promo.max_uses > 0 else '♾ Cheksiz'}",
        reply_markup=main_menu_kb("uz"),
        parse_mode="HTML",
    )
