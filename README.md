# Nexus Prime Bot v1.4.0 (Beta)

Discord-бот для управления мультивселенной Нексус Прайм

## Особенности:
- Автономный запуск с launcher.py
- Авто-обновление с GitHub
- Диагностика системы
- Умная система владельца

## Установка:
```bash
git clone https://github.com/VovaLoV2024/nexus-prime-bot.git 
cd nexus-prime-bot
python launcher.py
```

## Требования:
- Python 3.8+
- Discord.py
- Colorama

## Структура проекта:
```
nexus-prime-bot/
├── launcher.py              # Главный файл запуска (в корне!)
├── README.md                # Этот файл
├── .gitignore               # Игнорируемые файлы
└── nexus_core/              # Папка с файлами бота
    ├── VERSION.txt          # Версии лаунчера и бота
    ├── nexus_bot.py         # Основной код бота
    ├── nexus_config.json    # Конфигурация (не загружать на GitHub!)
    ├── nexus_config.example.json  # Пример конфигурации
    ├── nexus_setup.py       # Скрипт настройки
    ├── requirements.txt     # Зависимости Python
    └── nexus_server_config/ # Конфигурация сервера
        ├── nexus_roles.json     # Роли и разрешения
        └── nexus_channels.json  # Каналы и категории
```

## Команды бота:
- `!помощь` / `!commands` - Список всех команд
- `!пинг` - Проверка пинга бота
- `!инфо` - Информация о боте
- `!сервер` - Информация о текущем сервере
- `!прайм` - Установить себя владельцем бота
- `!статус` - Показать статус бота

## Настройка:
1. При первом запуске `launcher.py` запросит токен бота
2. Получите токен на [Discord Developer Portal](https://discord.com/developers/applications)
3. Создайте новое приложение → Bot → Reset Token
4. Включите Privileged Gateway Intents:
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT

## Коды ошибок:
- **Код 1**: Ошибка токена (неверный или истек)
- **Код 2**: Не включены Privileged Intents
- **Код 3**: Ошибка сети
- **Код 4**: Другая ошибка

## Авторы:
- **Вова (VovaLoV)** - создатель проекта
- **Рокси** 🐺 - помощница и вдохновитель
- **Qwen Coder** - разработчик

## Лицензия:
MIT License

---
**Nexus Prime Bot** - ваш надёжный помощник в Discord! 💜
