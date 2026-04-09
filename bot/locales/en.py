"""English translations."""

TEXTS = {
    "welcome": (
        "🎯 <b>OSON REKLAMA</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🇺🇿 Place ads in <b>1000+</b> Telegram\n"
        "channels and groups across Uzbekistan!\n\n"
        "✅ Search by region and district\n"
        "✅ Affordable prices — from <b>10,000 UZS</b>\n"
        "✅ Fast and reliable service\n"
        "✅ Earn income as a channel owner\n\n"
        "👇 <b>Choose to get started:</b>"
    ),
    "menu.main": "🏠 <b>Main Menu</b>\n\nChoose an option:",
    "menu.browse": "📢 Place an Ad",
    "menu.search": "🔍 Search",
    "menu.my_orders": "📋 My Orders",
    "menu.my_channels": "📺 My Channels & Groups",
    "menu.settings": "🌐 Change Language",
    "menu.about": "ℹ️ About",
    "menu.referral": "👥 Invite Friends",
    "menu.subscriptions": "🔄 Subscriptions",
    "menu.language": "🌐 Change Language",
    "menu.back": "⬅️ Back",
    "menu.home": "🏠 Main Menu",
    "menu.cancel": "❌ Cancel",
    "menu.suggestions": "💡 Suggestions",
    "lang.select": "🌐 Select language:",
    "lang.changed": "✅ Language changed: English 🇬🇧",
    "browse.select_region": "🗺 <b>Select a region:</b>",
    "browse.select_district": "📍 <b>{region} — Select a district:</b>",
    "browse.select_category": "📂 <b>Select a category:</b>",
    "browse.no_channels": "😔 No channels/groups here yet.\n\nComing soon!",
    "browse.channels_list": "📺 <b>{district} channels/groups:</b>\n\nTotal: {count}",
    "browse.all_categories": "📂 All categories",
    "channel.card": (
        "📺 <b>{title}</b>\n"
        "├ 👤 @{username}\n"
        "├ 📍 {district}, {region}\n"
        "├ 📂 {category}\n"
        "├ 👥 <b>{subscribers}</b> subscribers\n"
        "├ 👁 ~<b>{views}</b> views\n"
        "├ ⭐ Rating: {rating}\n"
        "└ {verified}\n\n"
        "💰 <b>Prices:</b>\n{pricing}"
    ),
    "channel.verified": "✅ Verified",
    "channel.not_verified": "⏳ Under review",
    "channel.price_line": "  • {format}: <b>{price} UZS</b>\n",
    "channel.order_btn": "🛒 Order Ad",
    "channel.similar": "📺 Similar channels",
    "order.select_format": "📝 <b>Select ad format:</b>\n\n{formats}",
    "order.send_text": "✍️ <b>Send your ad content:</b>\n\nYou can send text, photos, videos, or other media.",
    "order.send_date": "📅 <b>Send desired date:</b>\n\nExample: <code>2025-04-10</code>\nOr type \"Today\" / \"Tomorrow\".",
    "order.preview": (
        "📋 <b>Order Details:</b>\n\n"
        "📺 Channel: <b>{channel}</b>\n"
        "📝 Format: <b>{format}</b>\n"
        "💰 Price: <b>{price} UZS</b>\n"
        "📅 Date: <b>{date}</b>\n\n"
        "Confirm?"
    ),
    "order.confirm": "✅ Confirm",
    "order.cancel": "❌ Cancel",
    "order.created": "✅ <b>Order #{id} created!</b>\n\nWaiting for channel owner response.\nStatus: ⏳ Pending",
    "order.cancelled": "❌ Order cancelled.",
    "order.invalid_date": "⚠️ Invalid date format. Please try again:",
    "order.today": "Today",
    "order.tomorrow": "Tomorrow",
    "status.pending": "⏳ Pending",
    "status.accepted": "✅ Accepted",
    "status.payment_pending": "💳 Payment pending",
    "status.paid": "💰 Paid",
    "status.published": "📢 Published",
    "status.completed": "✅ Completed",
    "status.rejected": "❌ Rejected",
    "status.cancelled": "🚫 Cancelled",
    "my_orders.title": "📋 <b>My Orders:</b>",
    "my_orders.empty": "📭 You have no orders yet.",
    "my_orders.item": "#{id} | {channel} | {format}\n   💰 {price} UZS | {status}\n",
    "my_orders.cancel_btn": "🚫 Cancel",
    "my_orders.detail": (
        "📋 <b>Order #{id}</b>\n\n"
        "📺 Channel: <b>{channel}</b>\n"
        "📝 Format: <b>{format}</b>\n"
        "💰 Price: <b>{price} UZS</b>\n"
        "📅 Date: <b>{date}</b>\n"
        "📊 Status: {status}\n"
        "🕐 Created: {created}"
    ),
    "payment.info": "💳 <b>Payment details:</b>\n\nCard number: <code>{card}</code>\nAmount: <b>{amount} UZS</b>\n\nMake payment and\nsend screenshot here 📸",
    "payment.screenshot_received": "✅ Screenshot received!\n\nChannel owner will verify.\nPlease wait...",
    "payment.confirmed": "✅ Payment confirmed! Your ad will be published soon.",
    "payment.rejected": "❌ Payment rejected. Please contact admin.",
    "owner.panel": "📺 <b>My Channels & Groups:</b>",
    "owner.no_channels": "📭 You don't have channels or groups yet.\n\nAdd one and start receiving ad orders!",
    "owner.add_channel": "➕ Add Channel or Group",
    "owner.enter_username": "📝 <b>Enter channel or group username:</b>\n\nExample: <code>@my_channel</code> or <code>@my_group</code>\n\n⚠️ Bot must be an admin of the channel/group!",
    "owner.select_region": "📍 <b>Select region:</b>",
    "owner.select_district": "📍 <b>Select district:</b>",
    "owner.select_category": "📂 <b>Select category:</b>",
    "owner.enter_subscribers": "👥 <b>Enter number of subscribers/members:</b>\n\nExample: <code>5000</code>",
    "owner.enter_views": "👁 <b>Enter average views:</b>\n\nExample: <code>2000</code>",
    "owner.enter_description": "📝 <b>Enter description:</b>\n\nWrite a brief description about your channel.",
    "owner.set_prices": "💰 <b>Set ad prices:</b>\n\nEnter price for each format in UZS.\nIf format unavailable — enter 0.\n\nNow: <b>{format}</b>\nPrice (UZS):",
    "owner.channel_added": "✅ <b>Channel added!</b>\n\n📺 {title} (@{username})\n\nSent for moderation.\nWaiting for admin approval ⏳",
    "owner.invalid_number": "⚠️ Please enter a number.",
    "owner.invalid_username": "⚠️ Invalid username. Start with @.",
    "owner.enter_card": "💳 <b>Enter your card number:</b>\n\nAdvertisers will pay to this card.\nExample: <code>9860350149811860</code>",
    "owner.invalid_card": "⚠️ Invalid card number. Enter 16 digits.",
    "owner.incoming_orders": "📩 <b>Incoming orders:</b>",
    "owner.no_orders": "📭 No new orders yet.",
    "owner.accept_order": "✅ Accept",
    "owner.reject_order": "❌ Reject",
    "owner.enter_reject_reason": "📝 Enter rejection reason:",
    "owner.order_accepted": "✅ Order #{id} accepted! Advertiser notified.",
    "owner.order_rejected": "❌ Order #{id} rejected.",
    "owner.mark_published": "📢 Mark as published",
    "owner.manage_channel": "📺 <b>{title}</b> (@{username})\n\n👥 {subscribers} subscribers\n👁 ~{views} views\n📊 Status: {status}\n\nWhat would you like to do?",
    "owner.edit_prices": "💰 Edit prices",
    "owner.toggle_active": "🔄 Toggle active",
    "owner.delete_channel": "🗑 Delete",
    "owner.channel_deleted": "✅ Channel deleted.",
    "owner.channel_activated": "✅ Channel activated.",
    "owner.channel_deactivated": "⏸ Channel paused.",
    "owner.income_stats": "💰 <b>Today's income:</b> {daily} UZS\n📊 <b>Monthly income:</b> {monthly} UZS\n📋 <b>Commission (5%):</b> {commission} UZS",
    "admin.panel": "⚙️ <b>Admin Panel</b>\n\nSelect an option:",
    "admin.stats": "📊 Statistics",
    "admin.moderate": "✅ Moderation",
    "admin.broadcast": "📢 Broadcast",
    "admin.categories": "🗂 Categories",
    "admin.block_user": "🚫 Block user",
    "admin.all_orders": "📋 All orders",
    "admin.stats_text": "📊 <b>Statistics:</b>\n\n👥 Users: <b>{users}</b>\n📺 Channels: <b>{channels}</b>\n  ├ ✅ Verified: <b>{verified}</b>\n  └ ⏳ Pending: <b>{pending}</b>\n📋 Orders: <b>{orders}</b>\n  ├ Today: <b>{today_orders}</b>\n  └ This week: <b>{week_orders}</b>",
    "admin.moderate_list": "✅ <b>Channels pending moderation:</b>",
    "admin.no_pending": "📭 No pending channels.",
    "admin.approve_channel": "✅ Approve",
    "admin.reject_channel": "❌ Reject",
    "admin.channel_approved": "✅ Channel approved! Owner notified.",
    "admin.channel_rejected": "❌ Channel rejected.",
    "admin.broadcast_text": "📢 <b>Broadcast to all users:</b>\n\nSend message text:",
    "admin.broadcast_confirm": "📢 Send message to {count} users?",
    "admin.broadcast_done": "✅ Message sent to {sent}/{total} users.",
    "admin.confirm_payment": "✅ Confirm payment",
    "admin.reject_payment": "❌ Reject payment",
    "notify.new_order": "📩 <b>New order!</b>\n\n📺 Channel: {channel}\n📝 Format: {format}\n💰 Price: {price} UZS\n📅 Date: {date}\n👤 Advertiser: {advertiser}\n\nAccept?",
    "notify.order_accepted": "✅ <b>Your order was accepted!</b>\n\n📺 Channel: {channel}\n📝 Format: {format}\n💰 Price: {price} UZS\n\n💳 Please make payment.",
    "notify.order_rejected": "❌ <b>Your order was rejected.</b>\n\n📺 Channel: {channel}\n📝 Reason: {reason}",
    "notify.channel_approved": "✅ <b>Your channel is approved!</b>\n\n📺 {title} (@{username})\n\nYou can now receive orders!",
    "notify.channel_rejected": "❌ <b>Your channel was rejected.</b>\n\n📺 {title} (@{username})\nReason: {reason}",
    "about": "ℹ️ <b>Oson Reklama Bot</b>\n\n📢 Ad placement service in Telegram\nchannels across Uzbekistan.\n\n🤖 Bot: @oson_reklama_uz_bot\n📞 Contact: @C_Rosinant\n\n© 2026 Oson Reklama",
    "error": "⚠️ An error occurred. Please try again.",
    "cancelled": "❌ Cancelled.",
    "confirm_yes": "✅ Yes",
    "confirm_no": "❌ No",
    "page_info": "📄 {current}/{total}",
    "prev_page": "◀️",
    "next_page": "▶️",
    "loading": "⏳ Loading...",
    "access_denied": "🚫 Access denied.",
    "search.enter_query": "🔍 <b>Search</b>\n\nEnter channel name or username:",
    "search.too_short": "⚠️ Enter at least 2 characters.",
    "search.no_results": "😔 Nothing found. Try a different query.",
    "search.results": "🔍 <b>\"{query}\"</b> — {count} results:",
    "rating.request": "⭐ <b>Rate the channel!</b>\n\n📺 {channel}\n\nHow would you rate it?",
    "report.enter_views": "👁 Enter the number of views for the ad post:",
    "report.enter_reach": "📊 Enter the reach of the ad post:",
    "report.saved": "✅ <b>Report saved!</b>\n\n👁 Views: {views}\n📊 Reach: {reach}",
    "report.btn": "📊 Submit report",
    "promo.enter_code": "🏷 Enter promo code (or skip):",
    "promo.applied": "✅ Promo code applied! Discount: {discount} UZS",
    "promo.invalid": "⚠️ Invalid or expired promo code.",
    "promo.btn": "🏷 Enter promo code",
    "order.repeat": "🔄 Repeat order",
    "my_orders.stats": "📊 <b>Your statistics:</b>\n\n📋 Total orders: <b>{total_orders}</b>\n✅ Completed: <b>{completed}</b>\n💰 Total spent: <b>{total_spent} UZS</b>",
    "referral.panel": "👥 <b>Invite friends!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nFor each invited friend\nyou get <b>5,000 UZS</b> bonus! 🎁\n\n📊 <b>Statistics:</b>\n👥 Invited: <b>{count}</b>\n💰 Bonus balance: <b>{bonus} UZS</b>\n\n🔗 Your link:\n<code>{link}</code>",
    "referral.new_join": "🎉 <b>New friend joined!</b>\n\n👤 {name} joined via your link!\n👥 Total invited: {count}\n💰 Bonus: +{bonus} UZS",
    "referral.share_btn": "📤 Share with friends",
    "referral.copy_link": "📋 Click link below to copy",
    "sub.empty": "🔄 You have no subscriptions yet.",
    "sub.title": "🔄 <b>Your subscriptions:</b>",
    "sub.select_frequency": "📅 <b>Select subscription frequency:</b>\n\nAds will be placed automatically.",
    "sub.created": "✅ <b>Subscription created!</b>\n\n📅 Frequency: {frequency}\n💰 Per post: {price} UZS\n\nAds will be placed automatically.",
    "suggestions.enter_text": "💡 <b>Write your suggestion:</b>\n\nSend us your ideas and feedback.\nWe will definitely review them! 📝",
    "suggestions.sent": "✅ Your suggestion has been received! Thank you! 🙏",
    "suggestions.error": "⚠️ An error occurred. Please try again.",
}
