"""
Support chat handler — bidirectional messaging between user and admin.
User sends message → forwarded to admin with Reply button.
Admin replies → forwarded back to user.
Both can leave the chat.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb
from bot.config import settings

router = Router()

# In-memory store: admin_id -> user_id they are chatting with
_admin_chats: dict[int, int] = {}
# In-memory store: user_id -> admin_id they are chatting with
_user_chats: dict[int, int] = {}


class SupportStates(StatesGroup):
    waiting_message = State()  # User waiting to type first message
    in_chat = State()          # User is in active chat with admin


class AdminSupportStates(StatesGroup):
    in_chat = State()  # Admin is in active chat with user


def _admin_reply_kb(user_id: int) -> InlineKeyboardBuilder:
    """Inline button for admin to start replying to a user."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💬 Javob yozish",
        callback_data=f"support_reply:{user_id}",
    )
    builder.adjust(1)
    return builder


def _leave_chat_kb(lang: str = "uz"):
    """Reply keyboard with leave chat button."""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text("support.leave_chat", lang))],
        ],
        resize_keyboard=True,
    )


def _admin_leave_chat_kb():
    """Reply keyboard with leave chat button for admin."""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚪 Chatdan chiqish")],
        ],
        resize_keyboard=True,
    )


# ─── User sends first support message ───

@router.message(SupportStates.waiting_message)
async def receive_support_message(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    user = message.from_user
    username = f"@{user.username}" if user.username else "—"
    full_name = user.full_name or "—"

    # Build admin notification
    admin_text = (
        f"📩 <b>Qo'llab-quvvatlash xabari!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Foydalanuvchi:</b> {full_name}\n"
        f"🆔 Username: {username}\n"
        f"🔢 ID: <code>{user.id}</code>\n\n"
        f"💬 <b>Xabar:</b>\n{message.text or '(media)'}\n"
    )

    sent = False
    for admin_id in settings.admin_ids:
        try:
            # Forward the original message to admin
            await message.forward(chat_id=admin_id)
            # Send info card with reply button
            kb = _admin_reply_kb(user.id)
            await message.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=kb.as_markup(),
                parse_mode="HTML",
            )
            sent = True
        except Exception:
            continue

    if sent:
        # Put user into active chat mode
        await state.set_state(SupportStates.in_chat)
        await message.answer(
            get_text("about.support_sent", lang),
            reply_markup=_leave_chat_kb(lang),
            parse_mode="HTML",
        )
    else:
        await state.clear()
        await message.answer(
            get_text("about.support_error", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )


# ─── Admin clicks "Reply" button ───

@router.callback_query(F.data.startswith("support_reply:"))
async def admin_start_reply(
    callback: CallbackQuery, state: FSMContext, **kwargs
):
    admin_id = callback.from_user.id
    if admin_id not in settings.admin_ids:
        await callback.answer("⛔ Sizda ruxsat yo'q.")
        return

    user_id = int(callback.data.split(":")[1])

    # Link admin ↔ user
    _admin_chats[admin_id] = user_id
    _user_chats[user_id] = admin_id

    await state.set_state(AdminSupportStates.in_chat)
    await state.update_data(chat_user_id=user_id)

    await callback.message.answer(
        f"💬 <b>Chat boshlandi!</b>\n\n"
        f"Foydalanuvchi ID: <code>{user_id}</code>\n\n"
        f"Xabar yozing — u foydalanuvchiga yuboriladi.\n"
        f"Chiqish uchun «🚪 Chatdan chiqish» tugmasini bosing.",
        reply_markup=_admin_leave_chat_kb(),
        parse_mode="HTML",
    )
    await callback.answer("✅ Chat ochildi!")


# ─── Admin sends message in chat ───

@router.message(AdminSupportStates.in_chat)
async def admin_sends_message(
    message: Message, state: FSMContext, **kwargs
):
    admin_id = message.from_user.id

    # Check for leave command
    if message.text and message.text.strip() == "🚪 Chatdan chiqish":
        await _admin_leave(message, state)
        return

    data = await state.get_data()
    user_id = data.get("chat_user_id") or _admin_chats.get(admin_id)

    if not user_id:
        await state.clear()
        await message.answer("⚠️ Chat topilmadi.")
        return

    try:
        # Send admin's message to user
        admin_msg = (
            f"💬 <b>Admin javobi:</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{message.text or ''}"
        )
        await message.bot.send_message(
            chat_id=user_id,
            text=admin_msg,
            parse_mode="HTML",
        )
        await message.answer("✅ Xabar yuborildi!")
    except Exception:
        await message.answer("⚠️ Xabar yuborishda xatolik.")


# ─── User sends message while in chat ───

@router.message(SupportStates.in_chat)
async def user_sends_in_chat(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    # Check for leave command
    if message.text and message.text.strip() == get_text("support.leave_chat", lang):
        await _user_leave(message, state, lang)
        return

    user = message.from_user

    # Forward to all admins (or to linked admin)
    linked_admin = _user_chats.get(user.id)
    targets = [linked_admin] if linked_admin else settings.admin_ids

    sent = False
    for admin_id in targets:
        try:
            await message.forward(chat_id=admin_id)
            sent = True
        except Exception:
            continue

    if not sent:
        # Try all admins as fallback
        for admin_id in settings.admin_ids:
            try:
                await message.forward(chat_id=admin_id)
                sent = True
            except Exception:
                continue

    if sent:
        await message.answer(
            get_text("support.message_forwarded", lang),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            get_text("about.support_error", lang),
            parse_mode="HTML",
        )


# ─── Leave chat helpers ───

async def _admin_leave(message: Message, state: FSMContext):
    admin_id = message.from_user.id
    user_id = _admin_chats.pop(admin_id, None)
    if user_id:
        _user_chats.pop(user_id, None)
        # Notify user that admin left
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text="ℹ️ Admin chatni tugatdi. Rahmat! 🙏",
                parse_mode="HTML",
            )
        except Exception:
            pass

    await state.clear()

    from bot.keyboards.admin import admin_menu_kb
    await message.answer(
        "✅ Chatdan chiqdingiz.",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )


async def _user_leave(message: Message, state: FSMContext, lang: str = "uz"):
    user_id = message.from_user.id
    admin_id = _user_chats.pop(user_id, None)
    if admin_id:
        _admin_chats.pop(admin_id, None)

    await state.clear()
    await message.answer(
        get_text("support.chat_ended", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
