# Synapse Bot MVP v2.1

Telegram-бот на aiogram 3.x для Senapse

## Установка

1. Создайте виртуальное окружение:
   ```bash
   py -m venv venv
   ```

2. Активируйте виртуальное окружение:
   - Windows PowerShell: `venv\Scripts\Activate.ps1`
   - Windows CMD: `venv\Scripts\activate.bat`
   - Linux/Mac: `source venv/bin/activate`

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` и добавьте токен бота:
   ```
   BOT_TOKEN=ваш_токен_от_BotFather
   ```

## Запуск

```bash
python bot.py
```

или с виртуальным окружением:

```bash
venv\Scripts\python.exe bot.py
```

## Функционал

- Команда `/start` с поддержкой реферального кода
- Приветственное сообщение
- Inline кнопка "Активировать Триал" с Web App (TMA)
- Остальные сообщения игнорируются

## Структура проекта

```
senapse-mvp/
├── bot.py           # Основной код бота
├── .env            # Токен бота (не в git)
├── requirements.txt # Зависимости
├── .gitignore      # Игнорируемые файлы
└── venv/           # Виртуальное окружение
```

