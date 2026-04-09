"""Uzbek (Latin) translations."""

TEXTS = {
    # ─── Start & Menu ───
    "welcome": (
        "🎯 <b>OSON REKLAMA</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🇺🇿 O'zbekiston bo'ylab <b>1000+</b> Telegram\n"
        "kanallarda va guruhlarda reklama joylashtiring!\n\n"
        "✅ Viloyat va tuman bo'yicha qidiruv\n"
        "✅ Qulay narxlar — <b>10,000 so'mdan</b>\n"
        "✅ Tez va ishonchli xizmat\n"
        "✅ Kanal egalariga daromad\n\n"
        "👇 <b>Boshlash uchun tanlang:</b>"
    ),
    "menu.main": "🏠 <b>Bosh menyu</b>\n\nQuyidagilardan birini tanlang:",
    "menu.browse": "📢 Reklama joylashtirish",
    "menu.search": "🔍 Qidirish",
    "menu.my_orders": "📋 Mening buyurtmalarim",
    "menu.my_channels": "📺 Kanallarim va Guruhlarim",
    "menu.settings": "🌐 Tilni o'zgartirish",
    "menu.about": "ℹ️ Bot haqida",
    "menu.referral": "👥 Do'stlarni taklif qilish",
    "menu.subscriptions": "🔄 Obunalar",
    "menu.language": "🌐 Tilni o'zgartirish",
    "menu.back": "⬅️ Orqaga",
    "menu.home": "🏠 Bosh menyu",
    "menu.cancel": "❌ Bekor qilish",

    # ─── Language ───
    "lang.select": "🌐 Tilni tanlang / Выберите язык:",
    "lang.changed": "✅ Til o'zgartirildi: O'zbekcha 🇺🇿",

    # ─── Browse ───
    "browse.select_region": "🗺 <b>Viloyatni tanlang:</b>",
    "browse.select_district": "📍 <b>{region} — Tumanni tanlang:</b>",
    "browse.select_category": "📂 <b>Kategoriyani tanlang:</b>",
    "browse.no_channels": "😔 Hozircha bu yerda kanallar/guruhlar yo'q.\n\nTez orada qo'shiladi!",
    "browse.channels_list": "📺 <b>{district} kanallari/guruhlari:</b>\n\nJami: {count} ta",
    "browse.all_categories": "📂 Barcha kategoriyalar",

    # ─── Channel Card ───
    "channel.card": (
        "📺 <b>{title}</b>\n"
        "├ 👤 @{username}\n"
        "├ 📍 {district}, {region}\n"
        "├ 📂 {category}\n"
        "├ 👥 <b>{subscribers}</b> obunachi\n"
        "├ 👁 ~<b>{views}</b> ko'rish\n"
        "├ ⭐ Reyting: {rating}\n"
        "└ {verified}\n\n"
        "💰 <b>Narxlar:</b>\n{pricing}"
    ),
    "channel.verified": "✅ Tasdiqlangan",
    "channel.not_verified": "⏳ Moderatsiyada",
    "channel.price_line": "  • {format}: <b>{price} so'm</b>\n",
    "channel.order_btn": "🛒 Reklama buyurtma berish",
    "channel.similar": "📺 O'xshash kanallar",

    # ─── Order ───
    "order.select_format": "📝 <b>Reklama formatini tanlang:</b>\n\n{formats}",
    "order.send_text": (
        "✍️ <b>Reklama matnini yuboring:</b>\n\n"
        "Matn, rasm, video yoki boshqa media yuborishingiz mumkin."
    ),
    "order.send_date": (
        "📅 <b>Kerakli sanani yuboring:</b>\n\n"
        "Masalan: <code>2025-04-10</code>\n"
        "Yoki \"Bugun\" / \"Ertaga\" deb yozing."
    ),
    "order.preview": (
        "📋 <b>Buyurtma tafsilotlari:</b>\n\n"
        "📺 Kanal: <b>{channel}</b>\n"
        "📝 Format: <b>{format}</b>\n"
        "💰 Narx: <b>{price} so'm</b>\n"
        "📅 Sana: <b>{date}</b>\n\n"
        "Tasdiqlaysizmi?"
    ),
    "order.confirm": "✅ Tasdiqlash",
    "order.cancel": "❌ Bekor qilish",
    "order.created": (
        "✅ <b>Buyurtma #{id} yaratildi!</b>\n\n"
        "Kanal egasi javobini kuting.\n"
        "Status: ⏳ Kutilmoqda"
    ),
    "order.cancelled": "❌ Buyurtma bekor qilindi.",
    "order.invalid_date": "⚠️ Noto'g'ri sana formati. Qaytadan kiriting:",
    "order.today": "Bugun",
    "order.tomorrow": "Ertaga",

    # ─── Order Statuses ───
    "status.pending": "⏳ Kutilmoqda",
    "status.accepted": "✅ Qabul qilindi",
    "status.payment_pending": "💳 To'lov kutilmoqda",
    "status.paid": "💰 To'langan",
    "status.published": "📢 Chop etildi",
    "status.completed": "✅ Yakunlandi",
    "status.rejected": "❌ Rad etildi",
    "status.cancelled": "🚫 Bekor qilingan",

    # ─── My Orders ───
    "my_orders.title": "📋 <b>Mening buyurtmalarim:</b>",
    "my_orders.empty": "📭 Sizda hali buyurtmalar yo'q.",
    "my_orders.item": (
        "#{id} | {channel} | {format}\n"
        "   💰 {price} so'm | {status}\n"
    ),
    "my_orders.cancel_btn": "🚫 Bekor qilish",
    "my_orders.detail": (
        "📋 <b>Buyurtma #{id}</b>\n\n"
        "📺 Kanal: <b>{channel}</b>\n"
        "📝 Format: <b>{format}</b>\n"
        "💰 Narx: <b>{price} so'm</b>\n"
        "📅 Sana: <b>{date}</b>\n"
        "📊 Status: {status}\n"
        "🕐 Yaratilgan: {created}"
    ),

    # ─── Payment ───
    "payment.info": (
        "💳 <b>To'lov ma'lumotlari:</b>\n\n"
        "Karta raqami: <code>{card}</code>\n"
        "Summa: <b>{amount} so'm</b>\n\n"
        "To'lovni amalga oshiring va\n"
        "screenshotni shu yerga yuboring 📸"
    ),
    "payment.screenshot_received": (
        "✅ Screenshot qabul qilindi!\n\n"
        "Kanal egasi to'lovni tekshiradi.\n"
        "Kuting..."
    ),
    "payment.confirmed": "✅ To'lov tasdiqlandi! Reklama tez orada chop etiladi.",
    "payment.rejected": "❌ To'lov rad etildi. Iltimos, admin bilan bog'laning.",

    # ─── Channel Owner ───
    "owner.panel": "📺 <b>Mening kanallarim va guruhlarim:</b>",
    "owner.no_channels": (
        "📭 Sizda hali kanal yoki guruh yo'q.\n\n"
        "Kanalingizni qo'shing va reklama buyurtmalarini qabul qiling!"
    ),
    "owner.add_channel": "➕ Kanal yoki guruh qo'shish",
    "owner.enter_username": (
        "📝 <b>Kanal yoki guruh username kiriting:</b>\n\n"
        "Masalan: <code>@my_channel</code> yoki <code>@my_group</code>\n\n"
        "⚠️ Bot kanal yoki guruh adminlari ro'yxatida bo'lishi kerak!"
    ),
    "owner.select_region": "📍 <b>Viloyatni tanlang:</b>",
    "owner.select_district": "📍 <b>Tumanni tanlang:</b>",
    "owner.select_category": "📂 <b>Kategoriyani tanlang:</b>",
    "owner.enter_subscribers": (
        "👥 <b>A'zolar/obunachlar sonini kiriting:</b>\n\n"
        "Masalan: <code>5000</code>"
    ),
    "owner.enter_views": (
        "👁 <b>O'rtacha ko'rishlar sonini kiriting:</b>\n\n"
        "Masalan: <code>2000</code>"
    ),
    "owner.enter_description": (
        "📝 <b>Kanal tavsifini kiriting:</b>\n\n"
        "Qisqacha kanal haqida ma'lumot yozing."
    ),
    "owner.set_prices": (
        "💰 <b>Reklama narxlarini belgilang:</b>\n\n"
        "Har bir format uchun narxni so'mda kiriting.\n"
        "Agar format mavjud bo'lmasa — 0 kiriting.\n\n"
        "Hozir: <b>{format}</b>\n"
        "Narxi (so'mda):"
    ),
    "owner.channel_added": (
        "✅ <b>Kanal qo'shildi!</b>\n\n"
        "📺 {title} (@{username})\n\n"
        "Kanal moderatsiyaga yuborildi.\n"
        "Admin tasdiqlashi kutilmoqda ⏳"
    ),
    "owner.invalid_number": "⚠️ Iltimos, raqam kiriting.",
    "owner.invalid_username": "⚠️ Noto'g'ri username. @ bilan boshlang.",
    "owner.enter_card": (
        "💳 <b>Karta raqamingizni kiriting:</b>\n\n"
        "Reklama beruvchilar shu kartaga to'lov qiladi.\n"
        "Masalan: <code>9860350149811860</code>"
    ),
    "owner.invalid_card": "⚠️ Noto'g'ri karta raqami. 16 ta raqam kiriting.",
    "owner.incoming_orders": "📩 <b>Kiruvchi buyurtmalar:</b>",
    "owner.no_orders": "📭 Hozircha yangi buyurtmalar yo'q.",
    "owner.accept_order": "✅ Qabul qilish",
    "owner.reject_order": "❌ Rad etish",
    "owner.enter_reject_reason": "📝 Rad etish sababini kiriting:",
    "owner.order_accepted": "✅ Buyurtma #{id} qabul qilindi! Reklama beruvchiga xabar yuborildi.",
    "owner.order_rejected": "❌ Buyurtma #{id} rad etildi.",
    "owner.mark_published": "📢 Chop etildi deb belgilash",
    "owner.manage_channel": (
        "📺 <b>{title}</b> (@{username})\n\n"
        "👥 {subscribers} obunachi\n"
        "👁 ~{views} ko'rish\n"
        "📊 Status: {status}\n\n"
        "Nima qilmoqchisiz?"
    ),
    "owner.edit_prices": "💰 Narxlarni o'zgartirish",
    "owner.toggle_active": "🔄 Aktivni o'zgartirish",
    "owner.delete_channel": "🗑 O'chirish",
    "owner.channel_deleted": "✅ Kanal o'chirildi.",
    "owner.channel_activated": "✅ Kanal aktivlashtirildi.",
    "owner.channel_deactivated": "⏸ Kanal to'xtatildi.",
    "owner.income_stats": (
        "💰 <b>Bugungi daromad:</b> {daily} so'm\n"
        "📊 <b>Oylik daromad:</b> {monthly} so'm\n"
        "📋 <b>Komissiya (5%):</b> {commission} so'm"
    ),

    # ─── Admin ───
    "admin.panel": (
        "⚙️ <b>Admin panel</b>\n\n"
        "Quyidagilardan birini tanlang:"
    ),
    "admin.stats": "📊 Statistika",
    "admin.moderate": "✅ Moderatsiya",
    "admin.broadcast": "📢 Xabar yuborish",
    "admin.categories": "🗂 Kategoriyalar",
    "admin.block_user": "🚫 Foydalanuvchini bloklash",
    "admin.all_orders": "📋 Barcha buyurtmalar",
    "admin.stats_text": (
        "📊 <b>Statistika:</b>\n\n"
        "👥 Foydalanuvchilar: <b>{users}</b>\n"
        "📺 Kanallar: <b>{channels}</b>\n"
        "  ├ ✅ Tasdiqlangan: <b>{verified}</b>\n"
        "  └ ⏳ Kutilmoqda: <b>{pending}</b>\n"
        "📋 Buyurtmalar: <b>{orders}</b>\n"
        "  ├ Bugun: <b>{today_orders}</b>\n"
        "  └ Bu hafta: <b>{week_orders}</b>"
    ),
    "admin.moderate_list": "✅ <b>Moderatsiyada kutayotgan kanallar:</b>",
    "admin.no_pending": "📭 Kutayotgan kanallar yo'q.",
    "admin.approve_channel": "✅ Tasdiqlash",
    "admin.reject_channel": "❌ Rad etish",
    "admin.channel_approved": "✅ Kanal tasdiqlandi! Egasiga xabar yuborildi.",
    "admin.channel_rejected": "❌ Kanal rad etildi.",
    "admin.broadcast_text": "📢 <b>Barcha foydalanuvchilarga xabar:</b>\n\nXabar matnini yuboring:",
    "admin.broadcast_confirm": "📢 Xabar {count} foydalanuvchiga yuborilsinmi?",
    "admin.broadcast_done": "✅ Xabar {sent}/{total} foydalanuvchiga yuborildi.",
    "admin.confirm_payment": "✅ To'lovni tasdiqlash",
    "admin.reject_payment": "❌ To'lovni rad etish",

    # ─── Notifications ───
    "notify.new_order": (
        "📩 <b>Yangi buyurtma!</b>\n\n"
        "📺 Kanal: {channel}\n"
        "📝 Format: {format}\n"
        "💰 Narx: {price} so'm\n"
        "📅 Sana: {date}\n"
        "👤 Buyurtmachi: {advertiser}\n\n"
        "Qabul qilasizmi?"
    ),
    "notify.order_accepted": (
        "✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        "📺 Kanal: {channel}\n"
        "📝 Format: {format}\n"
        "💰 Narx: {price} so'm\n\n"
        "💳 Endi to'lovni amalga oshiring."
    ),
    "notify.order_rejected": (
        "❌ <b>Buyurtmangiz rad etildi.</b>\n\n"
        "📺 Kanal: {channel}\n"
        "📝 Sabab: {reason}"
    ),
    "notify.channel_approved": (
        "✅ <b>Kanalingiz tasdiqlandi!</b>\n\n"
        "📺 {title} (@{username})\n\n"
        "Endi buyurtmalar qabul qilishingiz mumkin!"
    ),
    "notify.channel_rejected": (
        "❌ <b>Kanalingiz rad etildi.</b>\n\n"
        "📺 {title} (@{username})\n"
        "Sabab: {reason}"
    ),

    # ─── About ───
    "about": (
        "ℹ️ <b>Oson Reklama Bot</b>\n\n"
        "📢 O'zbekiston bo'ylab Telegram kanallarda\n"
        "reklama joylashtirish xizmati.\n\n"
        "🤖 Bot: @oson_reklama_uz_bot\n"
        "📞 Aloqa: @C_Rosinant\n\n"
        "© 2026 Oson Reklama"
    ),

    # ─── Common ───
    "error": "⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
    "cancelled": "❌ Bekor qilindi.",
    "confirm_yes": "✅ Ha",
    "confirm_no": "❌ Yo'q",
    "page_info": "📄 {current}/{total}",
    "prev_page": "◀️",
    "next_page": "▶️",
    "loading": "⏳ Yuklanmoqda...",
    "access_denied": "🚫 Sizda ruxsat yo'q.",

    # ─── Search ───
    "search.enter_query": (
        "🔍 <b>Qidiruv</b>\n\n"
        "Kanal nomi yoki username kiriting:"
    ),
    "search.too_short": "⚠️ Kamida 2 ta belgi kiriting.",
    "search.no_results": "😔 Hech narsa topilmadi. Boshqa so'z bilan urinib ko'ring.",
    "search.results": "🔍 <b>\"{query}\"</b> bo'yicha {count} ta natija:",

    # ─── Rating ───
    "rating.request": (
        "⭐ <b>Kanalni baholang!</b>\n\n"
        "📺 {channel}\n\n"
        "Qanday baholaysiz?"
    ),

    # ─── Post Report ───
    "report.enter_views": "👁 Reklama postining ko'rishlar sonini kiriting:",
    "report.enter_reach": "📊 Reklama postining qamrovini (reach) kiriting:",
    "report.saved": (
        "✅ <b>Hisobot saqlandi!</b>\n\n"
        "👁 Ko'rishlar: {views}\n"
        "📊 Qamrov: {reach}"
    ),
    "report.btn": "📊 Hisobot yuborish",

    # ─── Promo ───
    "promo.enter_code": "🏷 Promokod bo'lsa, kiriting (yoki o'tkazish uchun davom eting):",
    "promo.applied": "✅ Promokod qo'llanildi! Chegirma: {discount} so'm",
    "promo.invalid": "⚠️ Noto'g'ri yoki muddati o'tgan promokod.",
    "promo.btn": "🏷 Promokod kiritish",

    # ─── Repeat ───
    "order.repeat": "🔄 Qayta buyurtma",

    # ─── Advertiser Stats ───
    "my_orders.stats": (
        "📊 <b>Sizning statistikangiz:</b>\n\n"
        "📋 Jami buyurtmalar: <b>{total_orders}</b>\n"
        "✅ Yakunlangan: <b>{completed}</b>\n"
        "💰 Jami sarflangan: <b>{total_spent} so'm</b>"
    ),

    # ─── Referral ───
    "referral.panel": (
        "👥 <b>Do'stlarni taklif qiling!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Har bir taklif qilingan do'st uchun\n"
        "siz <b>5,000 so'm</b> bonus olasiz! 🎁\n\n"
        "📊 <b>Statistika:</b>\n"
        "👥 Taklif qilingan: <b>{count}</b> ta\n"
        "💰 Bonus balans: <b>{bonus} so'm</b>\n\n"
        "🔗 Sizning havolangiz:\n"
        "<code>{link}</code>"
    ),
    "referral.new_join": (
        "🎉 <b>Yangi do'st qo'shildi!</b>\n\n"
        "👤 {name} sizning havolangiz orqali qo'shildi!\n"
        "👥 Jami taklif qilingan: {count} ta\n"
        "💰 Bonus: +{bonus} so'm"
    ),
    "referral.share_btn": "📤 Do'stlarga ulashish",
    "referral.copy_link": "📋 Havolani nusxalash uchun pastga qarang",


    # ─── Subscriptions ───
    "sub.empty": "🔄 Hozircha obunalaringiz yo'q.",
    "sub.title": "🔄 <b>Sizning obunalaringiz:</b>",
    "sub.select_frequency": (
        "📅 <b>Obuna chastotasini tanlang:</b>\n\n"
        "Reklama avtomatik ravishda joylashtiriladi."
    ),
    "sub.created": (
        "✅ <b>Obuna yaratildi!</b>\n\n"
        "📅 Chastota: {frequency}\n"
        "💰 Har bir post: {price} so'm\n\n"
        "Reklama avtomatik joylashtiriladi."
    ),
}
