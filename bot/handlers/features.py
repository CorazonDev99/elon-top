"""
Features handler:
- Terms acceptance
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.database.repositories import user_repo

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


