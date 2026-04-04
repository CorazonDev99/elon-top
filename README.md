# 📢 Oson Reklama Bot

Telegram-бот для размещения рекламы в каналах по всему Узбекистану.

## 🚀 Запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

### 3. Запуск бота

```bash
python -m bot.main
```

При первом запуске автоматически:
- Создаются таблицы в PostgreSQL
- Заполняются справочники (14 вилоятов, 170+ туманов, категории, форматы)

## 📁 Структура проекта

```
bot/
├── main.py              # Точка входа
├── config.py            # Настройки (Pydantic)
├── database/            # БД (SQLAlchemy + PostgreSQL)
│   ├── models.py        # Модели
│   ├── engine.py        # Движок
│   └── repositories/    # CRUD-операции
├── handlers/            # Обработчики команд
│   ├── start.py         # /start, меню, язык
│   ├── browse.py        # Каталог каналов
│   ├── order.py         # Создание заказа
│   ├── my_orders.py     # Мои заказы
│   ├── channel_owner.py # Панель владельца канала
│   └── admin.py         # Админ-панель
├── keyboards/           # Клавиатуры
├── states/              # FSM-состояния
├── middlewares/          # Middleware
├── locales/             # Локализация (UZ, RU)
├── data/                # Справочные данные
└── utils/               # Утилиты
```

## 🤖 Bot: @oson_reklama_uz_bot
