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
from sqlalchemy.orm import selectinload

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


async def guarantee_auto_refund(bot):
    """Auto-cancel orders paid > 48h ago but not published. Notify both sides."""
    logger.info("🛡 Checking guarantee (48h auto-refund)...")

    async with async_session() as session:
        from bot.database.models import Order
        from sqlalchemy import select

        cutoff = datetime.utcnow() - timedelta(hours=settings.guarantee_hours)

        result = await session.execute(
            select(Order)
            .where(
                Order.status == "paid",
                Order.updated_at < cutoff,
            )
        )
        overdue_orders = list(result.scalars().all())

        for order in overdue_orders:
            try:
                order.status = "cancelled"
                await session.commit()

                # Notify advertiser
                try:
                    await bot.send_message(
                        chat_id=order.advertiser_telegram_id,
                        text=(
                            f"🛡 <b>Garantiya ishladi!</b>\n\n"
                            f"Buyurtma #{order.id} — reklama {settings.guarantee_hours} soat ichida "
                            f"joylashtirilmadi.\n"
                            f"To'lov qaytariladi. Admin bilan bog'laning."
                        ),
                        parse_mode="HTML",
                    )
                except Exception:
                    pass

                # Notify channel owner
                if order.channel and order.channel.owner:
                    try:
                        await bot.send_message(
                            chat_id=order.channel.owner.telegram_id,
                            text=(
                                f"⚠️ <b>Buyurtma #{order.id} bekor qilindi!</b>\n\n"
                                f"Reklama {settings.guarantee_hours} soat ichida joylashtirilmadi.\n"
                                f"To'lov reklama beruvchiga qaytariladi."
                            ),
                            parse_mode="HTML",
                        )
                    except Exception:
                        pass

                # Notify admin
                for admin_id in settings.admin_ids:
                    try:
                        await bot.send_message(
                            chat_id=admin_id,
                            text=(
                                f"🛡 Guarantee refund\n\n"
                                f"Order #{order.id}\n"
                                f"Amount: {format_price(order.price)} UZS\n"
                                f"Reason: Not published in {settings.guarantee_hours}h"
                            ),
                        )
                    except Exception:
                        pass

                logger.info(f"Guarantee refund for order #{order.id}")

            except Exception as e:
                logger.error(f"Guarantee error for order #{order.id}: {e}")


async def send_top10_weekly(bot):
    """Send weekly TOP-10 channels broadcast every Monday."""
    today = date.today()
    if today.weekday() != 0:  # 0 = Monday
        return

    logger.info("🏅 Sending weekly TOP-10 broadcast...")

    async with async_session() as session:
        from bot.database.models import Channel
        from sqlalchemy import select

        result = await session.execute(
            select(Channel)
            .where(Channel.is_active == True, Channel.is_verified == True)
            .order_by(Channel.avg_rating.desc(), Channel.subscribers_count.desc())
            .limit(10)
        )
        top_channels = list(result.scalars().all())

        if not top_channels:
            return

        # Build UZ text
        text_uz = "🏅 <b>Haftalik TOP-10 kanallar!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        text_ru = "🏅 <b>Еженедельный ТОП-10 каналов!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"

        for i, ch in enumerate(top_channels, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            stars = f"⭐{ch.avg_rating}" if ch.avg_rating > 0 else ""
            subs = f"👥 {ch.subscribers_count:,}" if ch.subscribers_count else ""
            line = f"{medal} <b>{ch.channel_title}</b> @{ch.channel_username}\n     {subs} {stars}\n\n"
            text_uz += line
            text_ru += line

        text_uz += "📢 Reklama berish uchun botga yozing!"
        text_ru += "📢 Для размещения рекламы пишите боту!"

        # Send to all users
        users = await user_repo.get_all_users(session)
        sent = 0
        for user in users:
            try:
                text = text_uz if user.language == "uz" else text_ru
                await bot.send_message(chat_id=user.telegram_id, text=text, parse_mode="HTML")
                sent += 1
            except Exception:
                pass

        logger.info(f"🏅 TOP-10 sent to {sent} users")

        # Also post to bot channel
        if settings.bot_channel_id:
            try:
                await bot.send_message(
                    chat_id=settings.bot_channel_id,
                    text=text_uz,
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.error(f"Failed to post TOP-10 to channel: {e}")


async def process_subscriptions(bot):
    """Process due subscriptions — auto-create orders."""
    logger.info("🔄 Processing subscriptions...")

    async with async_session() as session:
        from bot.database.repositories import subscription_repo, order_repo

        due_subs = await subscription_repo.get_due_subscriptions(session)

        for sub in due_subs:
            try:
                # Create order from subscription
                order = await order_repo.create_order(
                    session,
                    advertiser_tid=sub.advertiser_telegram_id,
                    channel_id=sub.channel_id,
                    ad_format_id=sub.ad_format_id,
                    price=sub.price_per_post,
                    ad_text=sub.ad_text,
                    ad_media_file_id=sub.ad_media_file_id,
                    ad_media_type=sub.ad_media_type,
                    desired_date=date.today(),
                )

                # Advance next date
                await subscription_repo.advance_subscription(session, sub.id)

                # Notify advertiser
                adv_lang = sub.advertiser.language if sub.advertiser else "uz"
                ch_name = sub.channel.channel_title if sub.channel else "?"
                try:
                    await bot.send_message(
                        chat_id=sub.advertiser_telegram_id,
                        text=(
                            f"🔄 <b>Obuna buyurtmasi yaratildi!</b>\n\n"
                            f"📺 {ch_name}\n"
                            f"💰 {format_price(sub.price_per_post)} so'm\n"
                            f"📋 Buyurtma #{order.id}"
                        ) if adv_lang == "uz" else (
                            f"🔄 <b>Заказ по подписке создан!</b>\n\n"
                            f"📺 {ch_name}\n"
                            f"💰 {format_price(sub.price_per_post)} сум\n"
                            f"📋 Заказ #{order.id}"
                        ),
                        parse_mode="HTML",
                    )
                except Exception:
                    pass

                logger.info(f"Subscription #{sub.id} → Order #{order.id}")

            except Exception as e:
                logger.error(f"Subscription #{sub.id} error: {e}")


async def post_to_bot_channel(bot, text: str):
    """Helper: post a message to the bot's announcement channel."""
    if not settings.bot_channel_id:
        return
    try:
        await bot.send_message(
            chat_id=settings.bot_channel_id,
            text=text,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Failed to post to bot channel: {e}")


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
            await guarantee_auto_refund(bot)
            await send_top10_weekly(bot)
            await process_subscriptions(bot)
            await publish_recurring_ads(bot)
            logger.info("⏰ Scheduled tasks completed")

        except asyncio.CancelledError:
            logger.info("⏰ Scheduler stopped")
            break
        except Exception as e:
            logger.error(f"⏰ Scheduler error: {e}")
            await asyncio.sleep(3600)  # Retry in 1 hour


async def publish_recurring_ads(bot):
    """Publish recurring ads (weekly/monthly) — runs daily."""
    today = date.today()
    logger.info(f"📢 Checking recurring ads for {today}")

    async with async_session() as session:
        from sqlalchemy import select, and_
        from bot.database.models import Order, Channel

        # Find orders that:
        # 1. Status is "published" (active recurring)
        # 2. publish_end_date >= today (not expired)
        # 3. last_published_at < today (not yet published today)
        result = await session.execute(
            select(Order)
            .where(
                Order.status == "published",
                Order.publish_end_date >= today,
                Order.last_published_at < today,
            )
            .options(
                selectinload(Order.channel),
                selectinload(Order.ad_format),
                selectinload(Order.advertiser),
            )
        )
        orders = result.scalars().all()

        if not orders:
            logger.info("📢 No recurring ads to publish today")
            return

        logger.info(f"📢 Found {len(orders)} recurring ads to publish")

        for order in orders:
            try:
                channel_username = order.channel.channel_username
                chat = await bot.get_chat(f"@{channel_username}")
                bot_member = await bot.get_chat_member(chat.id, bot.id)

                if bot_member.status not in ("administrator", "creator"):
                    logger.warning(f"Bot is not admin in @{channel_username}, skipping")
                    continue

                # Publish the ad
                if order.ad_media_file_id:
                    media_type = order.ad_media_type or "photo"
                    if media_type == "photo":
                        await bot.send_photo(
                            chat_id=chat.id,
                            photo=order.ad_media_file_id,
                            caption=order.ad_text or "",
                            parse_mode="HTML",
                        )
                    elif media_type == "video":
                        await bot.send_video(
                            chat_id=chat.id,
                            video=order.ad_media_file_id,
                            caption=order.ad_text or "",
                            parse_mode="HTML",
                        )
                    elif media_type == "document":
                        await bot.send_document(
                            chat_id=chat.id,
                            document=order.ad_media_file_id,
                            caption=order.ad_text or "",
                            parse_mode="HTML",
                        )
                elif order.ad_text:
                    await bot.send_message(
                        chat_id=chat.id,
                        text=order.ad_text,
                        parse_mode="HTML",
                    )

                # Update tracking
                order.last_published_at = today
                order.publish_count = (order.publish_count or 0) + 1

                # Check if this was the last day
                if today >= order.publish_end_date:
                    order.status = "completed"
                    logger.info(f"📢 Order #{order.id} completed (all days published)")

                await session.commit()
                logger.info(
                    f"📢 Published recurring ad #{order.id} to @{channel_username} "
                    f"(day {order.publish_count}/{(order.publish_end_date - order.publish_start_date).days + 1})"
                )

                await asyncio.sleep(1)  # Rate limit

            except Exception as e:
                logger.error(f"📢 Failed to publish recurring ad #{order.id}: {e}")
