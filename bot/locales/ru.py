"""Russian translations."""

TEXTS = {
    # ─── Start & Menu ───
    "welcome": (
        "🎯 <b>OSON REKLAMA</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🇺🇿 Размещайте рекламу в <b>1000+</b>\n"
        "Telegram-каналах по всему Узбекистану!\n\n"
        "✅ Поиск по области и району\n"
        "✅ Доступные цены — <b>от 10,000 сум</b>\n"
        "✅ Быстрый и надёжный сервис\n"
        "✅ Доход для владельцев каналов\n\n"
        "👇 <b>Выберите действие:</b>"
    ),
    "menu.main": "🏠 <b>Главное меню</b>\n\nВыберите действие:",
    "menu.browse": "📢 Разместить рекламу",
    "menu.search": "🔍 Поиск",
    "menu.my_orders": "📋 Мои заказы",
    "menu.my_channels": "📺 Мои каналы и группы",
    "menu.settings": "🌐 Сменить язык",
    "menu.about": "ℹ️ О боте",
    "menu.referral": "👥 Пригласить друзей",
    "menu.subscriptions": "🔄 Подписки",
    "menu.language": "🌐 Сменить язык",
    "menu.back": "⬅️ Назад",
    "menu.home": "🏠 Главное меню",
    "menu.cancel": "❌ Отмена",
    "menu.suggestions": "💡 Предложения",

    # ─── Language ───
    "lang.select": "🌐 Tilni tanlang / Выберите язык:",
    "lang.changed": "✅ Язык изменён: Русский 🇷🇺",

    # ─── Browse ───
    "browse.select_region": "🗺 <b>Выберите область:</b>",
    "browse.select_district": "📍 <b>{region} — Выберите район:</b>",
    "browse.select_category": "📂 <b>Выберите категорию:</b>",
    "browse.no_channels": "😔 Пока здесь нет каналов/групп.\n\nСкоро появятся!",
    "browse.channels_list": "📺 <b>Каналы и группы: {district}</b>\n\nВсего: {count}",
    "browse.all_categories": "📂 Все категории",

    # ─── Channel Card ───
    "channel.card": (
        "📺 <b>{title}</b>\n"
        "├ 👤 @{username}\n"
        "├ 📍 {district}, {region}\n"
        "├ 📂 {category}\n"
        "├ 👥 <b>{subscribers}</b> подписчиков\n"
        "├ 👁 ~<b>{views}</b> просмотров\n"
        "├ ⭐ Рейтинг: {rating}\n"
        "└ {verified}\n\n"
        "💰 <b>Цены:</b>\n{pricing}"
    ),
    "channel.verified": "✅ Проверен",
    "channel.not_verified": "⏳ На модерации",
    "channel.price_line": "  • {format}: <b>{price} сум</b>\n",
    "channel.order_btn": "🛒 Заказать рекламу",
    "channel.similar": "📺 Похожие каналы",

    # ─── Order ───
    "order.select_format": "📝 <b>Выберите формат рекламы:</b>\n\n{formats}",
    "order.send_text": (
        "✍️ <b>Отправьте рекламный материал:</b>\n\n"
        "Можно отправить текст, фото, видео или другие медиа."
    ),
    "order.send_date": (
        "📅 <b>Укажите желаемую дату:</b>\n\n"
        "Например: <code>2025-04-10</code>\n"
        "Или напишите \"Сегодня\" / \"Завтра\"."
    ),
    "order.preview": (
        "📋 <b>Детали заказа:</b>\n\n"
        "📺 Канал: <b>{channel}</b>\n"
        "📝 Формат: <b>{format}</b>\n"
        "💰 Цена: <b>{price} сум</b>\n"
        "📅 Дата: <b>{date}</b>\n\n"
        "Подтверждаете?"
    ),
    "order.confirm": "✅ Подтвердить",
    "order.cancel": "❌ Отменить",
    "order.created": (
        "✅ <b>Заказ #{id} создан!</b>\n\n"
        "Ожидайте ответа владельца канала.\n"
        "Статус: ⏳ Ожидание"
    ),
    "order.cancelled": "❌ Заказ отменён.",
    "order.invalid_date": "⚠️ Неверный формат даты. Введите ещё раз:",
    "order.today": "Сегодня",
    "order.tomorrow": "Завтра",

    # ─── Order Statuses ───
    "status.pending": "⏳ Ожидание",
    "status.accepted": "✅ Принят",
    "status.payment_pending": "💳 Ожидание оплаты",
    "status.paid": "💰 Оплачен",
    "status.published": "📢 Опубликован",
    "status.completed": "✅ Завершён",
    "status.rejected": "❌ Отклонён",
    "status.cancelled": "🚫 Отменён",

    # ─── My Orders ───
    "my_orders.title": "📋 <b>Мои заказы:</b>",
    "my_orders.empty": "📭 У вас пока нет заказов.",
    "my_orders.item": (
        "#{id} | {channel} | {format}\n"
        "   💰 {price} сум | {status}\n"
    ),
    "my_orders.cancel_btn": "🚫 Отменить",
    "my_orders.detail": (
        "📋 <b>Заказ #{id}</b>\n\n"
        "📺 Канал: <b>{channel}</b>\n"
        "📝 Формат: <b>{format}</b>\n"
        "💰 Цена: <b>{price} сум</b>\n"
        "📅 Дата: <b>{date}</b>\n"
        "📊 Статус: {status}\n"
        "🕐 Создан: {created}"
    ),

    # ─── Payment ───
    "payment.info": (
        "💳 <b>Данные для оплаты:</b>\n\n"
        "Номер карты: <code>{card}</code>\n"
        "Сумма: <b>{amount} сум</b>\n\n"
        "Произведите оплату и отправьте\n"
        "скриншот сюда 📸"
    ),
    "payment.screenshot_received": (
        "✅ Скриншот получен!\n\n"
        "Владелец канала проверит оплату.\n"
        "Ожидайте..."
    ),
    "payment.confirmed": "✅ Оплата подтверждена! Реклама скоро будет опубликована.",
    "payment.rejected": "❌ Оплата отклонена. Свяжитесь с админом.",

    # ─── Channel Owner ───
    "owner.panel": "📺 <b>Мои каналы и группы:</b>",
    "owner.no_channels": (
        "📭 У вас пока нет каналов и групп.\n\n"
        "Добавьте канал или группу и начните принимать заказы!"
    ),
    "owner.add_channel": "➕ Добавить канал или группу",
    "owner.enter_username": (
        "📝 <b>Введите username канала или группы:</b>\n\n"
        "Например: <code>@my_channel</code> или <code>@my_group</code>\n\n"
        "⚠️ Бот должен быть администратором канала или группы!"
    ),
    "owner.select_region": "📍 <b>Выберите область:</b>",
    "owner.select_district": "📍 <b>Выберите район:</b>",
    "owner.select_category": "📂 <b>Выберите категорию:</b>",
    "owner.enter_subscribers": (
        "👥 <b>Введите кол-во участников/подписчиков:</b>\n\n"
        "Например: <code>5000</code>"
    ),
    "owner.enter_views": (
        "👁 <b>Введите среднее кол-во просмотров:</b>\n\n"
        "Например: <code>2000</code>"
    ),
    "owner.enter_description": (
        "📝 <b>Введите описание канала:</b>\n\n"
        "Кратко опишите канал."
    ),
    "owner.set_prices": (
        "💰 <b>Установите цены на рекламу:</b>\n\n"
        "Для каждого формата укажите цену в сум.\n"
        "Если формат не предоставляется — введите 0.\n\n"
        "Сейчас: <b>{format}</b>\n"
        "Цена (в сум):"
    ),
    "owner.channel_added": (
        "✅ <b>Канал добавлен!</b>\n\n"
        "📺 {title} (@{username})\n\n"
        "Канал отправлен на модерацию.\n"
        "Ожидайте подтверждения админа ⏳"
    ),
    "owner.invalid_number": "⚠️ Пожалуйста, введите число.",
    "owner.invalid_username": "⚠️ Неверный username. Начните с @.",
    "owner.enter_card": (
        "💳 <b>Введите номер вашей карты:</b>\n\n"
        "Рекламодатели будут переводить оплату на эту карту.\n"
        "Например: <code>9860350149811860</code>"
    ),
    "owner.invalid_card": "⚠️ Неверный номер карты. Введите 16 цифр.",
    "owner.incoming_orders": "📩 <b>Входящие заказы:</b>",
    "owner.no_orders": "📭 Пока новых заказов нет.",
    "owner.accept_order": "✅ Принять",
    "owner.reject_order": "❌ Отклонить",
    "owner.enter_reject_reason": "📝 Введите причину отклонения:",
    "owner.order_accepted": "✅ Заказ #{id} принят! Рекламодатель уведомлён.",
    "owner.order_rejected": "❌ Заказ #{id} отклонён.",
    "owner.mark_published": "📢 Отметить как опубликовано",
    "owner.manage_channel": (
        "📺 <b>{title}</b> (@{username})\n\n"
        "👥 {subscribers} подписчиков\n"
        "👁 ~{views} просмотров\n"
        "📊 Статус: {status}\n\n"
        "Что хотите сделать?"
    ),
    "owner.edit_prices": "💰 Изменить цены",
    "owner.toggle_active": "🔄 Вкл/Выкл",
    "owner.delete_channel": "🗑 Удалить",
    "owner.channel_deleted": "✅ Канал удалён.",
    "owner.channel_activated": "✅ Канал активирован.",
    "owner.channel_deactivated": "⏸ Канал приостановлен.",
    "owner.income_stats": (
        "💰 <b>Доход за сегодня:</b> {daily} сум\n"
        "📊 <b>Месячный доход:</b> {monthly} сум\n"
        "📋 <b>Комиссия (5%):</b> {commission} сум"
    ),

    # ─── Admin ───
    "admin.panel": (
        "⚙️ <b>Админ-панель</b>\n\n"
        "Выберите действие:"
    ),
    "admin.stats": "📊 Статистика",
    "admin.moderate": "✅ Модерация",
    "admin.broadcast": "📢 Рассылка",
    "admin.categories": "🗂 Категории",
    "admin.block_user": "🚫 Блокировка",
    "admin.all_orders": "📋 Все заказы",
    "admin.stats_text": (
        "📊 <b>Статистика:</b>\n\n"
        "👥 Пользователи: <b>{users}</b>\n"
        "📺 Каналы: <b>{channels}</b>\n"
        "  ├ ✅ Проверены: <b>{verified}</b>\n"
        "  └ ⏳ Ожидают: <b>{pending}</b>\n"
        "📋 Заказы: <b>{orders}</b>\n"
        "  ├ Сегодня: <b>{today_orders}</b>\n"
        "  └ За неделю: <b>{week_orders}</b>"
    ),
    "admin.moderate_list": "✅ <b>Каналы на модерации:</b>",
    "admin.no_pending": "📭 Нет каналов на модерации.",
    "admin.approve_channel": "✅ Одобрить",
    "admin.reject_channel": "❌ Отклонить",
    "admin.channel_approved": "✅ Канал одобрен! Владелец уведомлён.",
    "admin.channel_rejected": "❌ Канал отклонён.",
    "admin.broadcast_text": "📢 <b>Рассылка всем пользователям:</b>\n\nОтправьте текст сообщения:",
    "admin.broadcast_confirm": "📢 Отправить сообщение {count} пользователям?",
    "admin.broadcast_done": "✅ Сообщение отправлено {sent}/{total} пользователям.",
    "admin.confirm_payment": "✅ Подтвердить оплату",
    "admin.reject_payment": "❌ Отклонить оплату",

    # ─── Notifications ───
    "notify.new_order": (
        "📩 <b>Новый заказ!</b>\n\n"
        "📺 Канал: {channel}\n"
        "📝 Формат: {format}\n"
        "💰 Цена: {price} сум\n"
        "📅 Дата: {date}\n"
        "👤 Заказчик: {advertiser}\n\n"
        "Принимаете?"
    ),
    "notify.order_accepted": (
        "✅ <b>Ваш заказ принят!</b>\n\n"
        "📺 Канал: {channel}\n"
        "📝 Формат: {format}\n"
        "💰 Цена: {price} сум\n\n"
        "💳 Теперь произведите оплату."
    ),
    "notify.order_rejected": (
        "❌ <b>Ваш заказ отклонён.</b>\n\n"
        "📺 Канал: {channel}\n"
        "📝 Причина: {reason}"
    ),
    "notify.channel_approved": (
        "✅ <b>Ваш канал одобрен!</b>\n\n"
        "📺 {title} (@{username})\n\n"
        "Теперь вы можете принимать заказы!"
    ),
    "notify.channel_rejected": (
        "❌ <b>Ваш канал отклонён.</b>\n\n"
        "📺 {title} (@{username})\n"
        "Причина: {reason}"
    ),

    # ─── About ───
    "about": (
        "ℹ️ <b>Oson Reklama Bot</b>\n\n"
        "📢 Сервис размещения рекламы в\n"
        "Telegram-каналах по всему Узбекистану.\n\n"
        "🤖 Бот: @oson_reklama_uz_bot\n"
        "📞 Контакт: @C_Rosinant\n\n"
        "© 2026 Oson Reklama"
    ),

    # ─── Common ───
    "error": "⚠️ Произошла ошибка. Попробуйте ещё раз.",
    "cancelled": "❌ Отменено.",
    "confirm_yes": "✅ Да",
    "confirm_no": "❌ Нет",
    "page_info": "📄 {current}/{total}",
    "prev_page": "◀️",
    "next_page": "▶️",
    "loading": "⏳ Загрузка...",
    "access_denied": "🚫 Доступ запрещён.",

    # ─── Search ───
    "search.enter_query": (
        "🔍 <b>Поиск</b>\n\n"
        "Введите название канала или username:"
    ),
    "search.too_short": "⚠️ Введите минимум 2 символа.",
    "search.no_results": "😔 Ничего не найдено. Попробуйте другой запрос.",
    "search.results": "🔍 <b>\"{query}\"</b> — {count} результат(ов):",

    # ─── Rating ───
    "rating.request": (
        "⭐ <b>Оцените канал!</b>\n\n"
        "📺 {channel}\n\n"
        "Как оцениваете?"
    ),

    # ─── Post Report ───
    "report.enter_views": "👁 Введите кол-во просмотров рекламного поста:",
    "report.enter_reach": "📊 Введите охват (reach) поста:",
    "report.saved": (
        "✅ <b>Отчёт сохранён!</b>\n\n"
        "👁 Просмотры: {views}\n"
        "📊 Охват: {reach}"
    ),
    "report.btn": "📊 Отправить отчёт",

    # ─── Promo ───
    "promo.enter_code": "🏷 Если есть промокод, введите (или пропустите):",
    "promo.applied": "✅ Промокод применён! Скидка: {discount} сум",
    "promo.invalid": "⚠️ Неверный или истёкший промокод.",
    "promo.btn": "🏷 Ввести промокод",

    # ─── Repeat ───
    "order.repeat": "🔄 Повторить заказ",

    # ─── Advertiser Stats ───
    "my_orders.stats": (
        "📊 <b>Ваша статистика:</b>\n\n"
        "📋 Всего заказов: <b>{total_orders}</b>\n"
        "✅ Завершенных: <b>{completed}</b>\n"
        "💰 Всего потрачено: <b>{total_spent} сум</b>"
    ),

    # ─── Referral ───
    "referral.panel": (
        "👥 <b>Пригласите друзей!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "За каждого приглашённого друга\n"
        "вы получаете <b>5,000 сум</b> бонус! 🎁\n\n"
        "📊 <b>Статистика:</b>\n"
        "👥 Приглашено: <b>{count}</b>\n"
        "💰 Бонус: <b>{bonus} сум</b>\n\n"
        "🔗 Ваша ссылка:\n"
        "<code>{link}</code>"
    ),
    "referral.new_join": (
        "🎉 <b>Новый друг присоединился!</b>\n\n"
        "👤 {name} присоединился по вашей ссылке!\n"
        "👥 Всего приглашено: {count}\n"
        "💰 Бонус: +{bonus} сум"
    ),
    "referral.share_btn": "📤 Поделиться с друзьями",
    "referral.copy_link": "📋 Нажмите ссылку ниже для копирования",


    # ─── Subscriptions ───
    "sub.empty": "🔄 У вас пока нет подписок.",
    "sub.title": "🔄 <b>Ваши подписки:</b>",
    "sub.select_frequency": (
        "📅 <b>Выберите частоту подписки:</b>\n\n"
        "Реклама будет размещаться автоматически."
    ),
    "sub.created": (
        "✅ <b>Подписка создана!</b>\n\n"
        "📅 Частота: {frequency}\n"
        "💰 За пост: {price} сум\n\n"
        "Реклама будет размещаться автоматически."
    ),

    # ─── Suggestions ───
    "suggestions.enter_text": (
        "💡 <b>Напишите ваше предложение:</b>\n\n"
        "Отправьте нам свои идеи и пожелания.\n"
        "Мы обязательно их рассмотрим! 📝"
    ),
    "suggestions.sent": "✅ Ваше предложение принято! Спасибо! 🙏",
    "suggestions.error": "⚠️ Произошла ошибка. Попробуйте ещё раз.",
}
