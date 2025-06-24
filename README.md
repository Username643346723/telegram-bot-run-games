# Telegram Bot Token Manager

Бот для управления и проверки токенов Telegram ботов.

## Функционал

✅ Проверка валидности токенов ботов  
✅ Хранение информации о токенах в БД  
✅ Поиск и фильтрация токенов  
✅ Статистика и отчеты  
✅ Админ-панель с интерактивным меню  

## Технологии

- Python 3.12
- Aiogram 3.x
- SQLAlchemy 2.0
- SQLite (или другая СУБД)
- Alembic для миграций

## Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/yourusername/telegram-bot-token-manager.git
cd telegram-bot-token-manager
`

.
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── bot/
│   ├── crud/               # Специфичные CRUD-операции бота
│   ├── filters/            # Фильтры aiogram
│   ├── handlers/           # Все обработчики команд
│   ├── middlewares/        # Прослойки бота
│   ├── models/             # Специфичные модели бота
│   ├── services/           # Сервисы бота
│   └── main.py             # Точка входа (polling)
├── core/
│   ├── bot/
│   │   └── __init__.py     # Инициализация bot и dp
│   ├── config/
│   │   ├── app.py          # Основные настройки приложения
│   │   ├── db.py           # Настройки БД
│   │   └── __init__.py     # Экспорт settings
│   ├── db/
│   │   ├── session.py      # DatabaseHelper
│   │   ├── models/         # Общие модели
│   │   └── __init__.py
│   ├── schemas/            # Pydantic схемы
│   └── services/           # Общие сервисы
├── libs/
│   └── logging/
│       ├── __init__.py     # setup_logger
│       └── logger.py       # Конфигурация логгера
├── webhook/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/  # Роутеры FastAPI
│   ├── dependencies/       # FastAPI зависимости
│   ├── services/           # Сервисы вебхуков
│   └── main.py            # Точка входа (FastAPI)
└── tests/
    ├── unit/              # Юнит-тесты
    ├── integration/       # Интеграционные тесты
    └── fixtures/          # Тестовые данные


sudo lsof -i :8080