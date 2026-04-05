"""
Scheduler — runs daily tasks:
1. Last 3 days of month: send commission reminders to channel owners
2. 1st day of new month: auto-deactivate channels of owners who didn't pay
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from calendar import monthrange

from bot.database.engine import async_session
from bot.database.repositories import commission_repo, user_repo
from bot.utils.formatting import format_price
from bot.config import settings

logger = logging.getLogger(__name__)


async def send_commission_reminders(bot):
    """Send reminders to channel owners about 5% commission in last 3 days of month."""
    today = date.today()
    _, last_day = monthrange(today.year, today.month)
    days_left = last_day - today.day

    if days_left > 2:
        # Not in last 3 days yet
        return

    logger.info(f"📢 Sending commission reminders (days left: {days_left + 1})")

    async with async_session() as session:
        owners = await commission_repo.get_all_channel_owners(session)

        for owner_tid in owners:
            try:
                income = await commission_repo.calculate_owner_monthly_income(
                    session, owner_tid, today.year, today.month
                )

                if income <= 0:
                    continue

                commission = await commission_repo.get_or_create_commission(
                    session, owner_tid, today.year, today.month
                )

                if commission.is_paid:
                    continue

                commission_amount = int(income * 0.05)

                # Format admin card
                card = settings.admin_card_number
                card_display = " ".join([card[i:i+4] for i in range(0, len(card), 4)])

                if days_left == 0:
                    urgency = "🔴 BUGUN OXIRGI KUN!"
                elif days_left == 1:
                    urgency = "🟡 Ertaga oxirgi kun!"
                else:
                    urgency = f"⚠️ {days_left + 1} kun qoldi"

                user = await user_repo.get_user(session, owner_tid)
                user_lang = user.language if user else "uz"

                if user_lang == "ru":
                    text = (
                        f"💰 <b>Ежемесячная комиссия</b>\n\n"
                        f"{urgency}\n\n"
                        f"📊 Ваш доход за {today.strftime('%B %Y')}: "
                        f"<b>{format_price(income)} сум</b>\n"
                        f"📋 Комиссия (5%): <b>{format_price(commission_amount)} сум</b>\n\n"
                        f"💳 Карта для оплаты:\n"
                        f"<code>{card_display}</code>\n\n"
                        f"⚠️ При неоплате ваши каналы будут деактивированы!"
                    )
                else:
                    text = (
                        f"💰 <b>Oylik komissiya</b>\n\n"
                        f"{urgency}\n\n"
                        f"📊 {today.strftime('%B %Y')} daromadingiz: "
                        f"<b>{format_price(income)} so'm</b>\n"
                        f"📋 Komissiya (5%): <b>{format_price(commission_amount)} so'm</b>\n\n"
                        f"💳 To'lov uchun karta:\n"
                        f"<code>{card_display}</code>\n\n"
                        f"⚠️ To'lanmasa kanallaringiz o'chiriladi!"
                    )

                await bot.send_message(
                    chat_id=owner_tid,
                    text=text,
                    parse_mode="HTML",
                )
                logger.info(f"Reminder sent to {owner_tid}")

            except Exception as e:
                logger.error(f"Failed to send reminder to {owner_tid}: {e}")


async def auto_deactivate_overdue(bot):
    """On 1st day of month: deactivate channels of owners who didn't pay last month's commission."""
    today = date.today()

    if today.day != 1:
        return

    logger.info("🔴 Running auto-deactivation for overdue commissions...")

    # Check last month
    if today.month == 1:
        check_year = today.year - 1
        check_month = 12
    else:
        check_year = today.year
        check_month = today.month - 1

    async with async_session() as session:
        owners = await commission_repo.get_all_channel_owners(session)

        for owner_tid in owners:
            try:
                income = await commission_repo.calculate_owner_monthly_income(
                    session, owner_tid, check_year, check_month
                )

                if income <= 0:
                    continue

                commission = await commission_repo.get_or_create_commission(
                    session, owner_tid, check_year, check_month
                )

                if commission.is_paid:
                    continue

                # Not paid — deactivate all channels
                from bot.database.models import Channel
                from sqlalchemy import select

                channels_result = await session.execute(
                    select(Channel).where(
                        Channel.owner_telegram_id == owner_tid,
                        Channel.is_active == True,
                    )
                )
                channels = channels_result.scalars().all()
                count = 0
                for ch in channels:
                    ch.is_active = False
                    count += 1

                if count > 0:
                    await session.commit()

                    user = await user_repo.get_user(session, owner_tid)
                    user_lang = user.language if user else "uz"

                    if user_lang == "ru":
                        text = (
                            f"🔴 <b>Каналы деактивированы!</b>\n\n"
                            f"Вы не оплатили комиссию за {check_month:02d}/{check_year}.\n"
                            f"Деактивировано каналов: {count}\n\n"
                            f"Оплатите комиссию и свяжитесь с админом для восстановления."
                        )
                    else:
                        text = (
                            f"🔴 <b>Kanallaringiz o'chirildi!</b>\n\n"
                            f"{check_month:02d}/{check_year} uchun komissiya to'lanmagan.\n"
                            f"O'chirilgan kanallar: {count}\n\n"
                            f"Komissiyani to'lang va qayta yoqish uchun admin bilan bog'laning."
                        )

                    await bot.send_message(
                        chat_id=owner_tid,
                        text=text,
                        parse_mode="HTML",
                    )

                    # Notify bot admin
                    for admin_id in settings.admin_ids:
                        try:
                            await bot.send_message(
                                chat_id=admin_id,
                                text=(
                                    f"🔴 Auto-deactivation\n\n"
                                    f"Owner: {user.full_name if user else owner_tid}\n"
                                    f"Channels deactivated: {count}\n"
                                    f"Reason: Unpaid commission {check_month:02d}/{check_year}"
                                ),
                                parse_mode="HTML",
                            )
                        except Exception:
                            pass

                    logger.info(f"Deactivated {count} channels for owner {owner_tid}")

            except Exception as e:
                logger.error(f"Failed to process deactivation for {owner_tid}: {e}")


async def remind_unpublished(bot):
    """Remind channel owners about orders paid > 24h ago but not yet published."""
    logger.info("🔔 Checking for unpublished orders...")

    async with async_session() as session:
        from bot.database.repositories import order_repo

        overdue = await order_repo.get_overdue_unpublished(session)

        for order in overdue:
            try:
                if not order.channel or not order.channel.owner:
                    continue

                owner_tid = order.channel.owner.telegram_id
                owner_lang = order.channel.owner.language or "uz"

                if owner_lang == "ru":
                    text = (
                        f"🔔 <b>Напоминание!</b>\n\n"
                        f"Заказ #{order.id} оплачен, но реклама ещё не опубликована.\n"
                        f"Канал: @{order.channel.channel_username}\n\n"
                        f"Пожалуйста, опубликуйте рекламу!"
                    )
                else:
                    text = (
                        f"🔔 <b>Eslatma!</b>\n\n"
                        f"Buyurtma #{order.id} to'langan, lekin reklama hali chop etilmagan.\n"
                        f"Kanal: @{order.channel.channel_username}\n\n"
                        f"Iltimos, reklamani chop eting!"
                    )

                await bot.send_message(
                    chat_id=owner_tid,
                    text=text,
                    parse_mode="HTML",
                )
                logger.info(f"Publish reminder sent for order #{order.id}")

            except Exception as e:
                logger.error(f"Failed to send publish reminder for order #{order.id}: {e}")


async def scheduler_loop(bot):
    """Main scheduler loop — runs once daily at ~10:00 UTC+5."""
    logger.info("⏰ Scheduler started")

    while True:
        try:
            # Calculate time until next 10:00 AM (UTC+5)
            now = datetime.utcnow()
            target_hour_utc = 5  # 10:00 UTC+5 = 05:00 UTC

            next_run = now.replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)
            if now.hour >= target_hour_utc:
                next_run += timedelta(days=1)

            wait_seconds = (next_run - now).total_seconds()
            logger.info(f"⏰ Next scheduler run in {wait_seconds / 3600:.1f} hours")

            await asyncio.sleep(wait_seconds)

            # Run tasks
            logger.info("⏰ Running scheduled tasks...")
            await send_commission_reminders(bot)
            await auto_deactivate_overdue(bot)
            await remind_unpublished(bot)
            logger.info("⏰ Scheduled tasks completed")

        except asyncio.CancelledError:
            logger.info("⏰ Scheduler stopped")
            break
        except Exception as e:
            logger.error(f"⏰ Scheduler error: {e}")
            await asyncio.sleep(3600)  # Retry in 1 hour
