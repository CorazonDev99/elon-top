"""
/start handler — welcome message, main menu, language selection, settings, about.
"""

import os

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text, LANGUAGES, menu_match
from bot.keyboards.main_menu import main_menu_kb, settings_kb
from bot.keyboards.admin import language_select_kb, admin_menu_kb
from bot.database.repositories import user_repo
from bot.database.models import User
from bot.config import settings

router = Router()

# Cache the file_id after first upload
_welcome_photo_file_id = None


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    global _welcome_photo_file_id
    await state.clear()

    caption = get_text("welcome", lang)

    # Notify referrer if this is a new referral
    referrer = kwargs.get("referrer")
    if referrer:
        try:
            ref_lang = referrer.language or "uz"
            await message.bot.send_message(
                chat_id=referrer.telegram_id,
                text=get_text(
                    "referral.new_join", ref_lang,
                    name=message.from_user.full_name or "—",
                    count=referrer.referral_count,
                    bonus="5,000",
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    try:
        if _welcome_photo_file_id:
            # Use cached file_id (faster)
            await message.answer_photo(
                photo=_welcome_photo_file_id,
                caption=caption,
                reply_markup=main_menu_kb(lang),
                parse_mode="HTML",
            )
        else:
            # First time — upload from file
            banner_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "bot", "assets", "welcome_banner.png"
            )
            if not os.path.exists(banner_path):
                # Fallback: try relative to project root
                banner_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "assets", "welcome_banner.png"
                )

            if os.path.exists(banner_path):
                photo = FSInputFile(banner_path)
                msg = await message.answer_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=main_menu_kb(lang),
                    parse_mode="HTML",
                )
                # Cache file_id for faster subsequent sends
                if msg.photo:
                    _welcome_photo_file_id = msg.photo[-1].file_id
            else:
                # No banner file — fallback to text
                await message.answer(
                    caption,
                    reply_markup=main_menu_kb(lang),
                    parse_mode="HTML",
                )
    except Exception:
        # Any error — fallback to text
        await message.answer(
            caption,
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )


@router.message(F.text.in_(menu_match("menu.browse")))
async def browse_menu(message: Message, lang: str = "uz", **kwargs):
    # Handled by browse.py — this import triggers region selection
    from bot.handlers.browse import show_regions
    await show_regions(message, lang=lang, **kwargs)


@router.message(F.text.in_(menu_match("menu.my_orders")))
async def my_orders_menu(message: Message, lang: str = "uz", **kwargs):
    from bot.handlers.my_orders import show_my_orders
    await show_my_orders(message, lang=lang, **kwargs)


@router.message(F.text.in_(menu_match("menu.my_channels")))
async def my_channels_menu(message: Message, lang: str = "uz", **kwargs):
    from bot.handlers.channel_owner import show_my_channels
    await show_my_channels(message, lang=lang, **kwargs)


@router.message(F.text.in_(menu_match("menu.settings")))
async def settings_menu(message: Message, lang: str = "uz", **kwargs):
    await message.answer(
        get_text("lang.select", lang),
        reply_markup=language_select_kb(),
        parse_mode="HTML",
    )


@router.message(F.text.in_(menu_match("menu.language")))
async def change_language(message: Message, **kwargs):
    await message.answer(
        get_text("lang.select"),
        reply_markup=language_select_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(
    callback: CallbackQuery,
    session: AsyncSession,
    **kwargs,
):
    lang = callback.data.split(":")[1]
    await user_repo.update_language(session, callback.from_user.id, lang)
    await callback.message.edit_text(
        get_text("lang.changed", lang),
        parse_mode="HTML",
    )
    await callback.message.answer(
        get_text("menu.main", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(F.text.in_(menu_match("menu.about")))
async def about(message: Message, lang: str = "uz", **kwargs):
    await message.answer(
        get_text("about", lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_(menu_match("menu.home")))
async def home(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    await state.clear()
    await message.answer(
        get_text("menu.main", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )

