# bot.py — 100% РАБОЧИЙ КОД (aiogram 3.x)
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

# === ТОКЕН ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле!")

# === TMA URL ===
TMA_URL = "https://google.com"

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)

# === БОТ ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === ТЕКСТ ===
WELCOME_TEXT = "Добро пожаловать в Synapse! Готовы получить профессиональный лидген в Telegram? Начнем."

# === /start ===
@dp.message(Command('start'))
async def start_command(message: types.Message):
    # Получаем ref_code из аргументов команды или используем "direct"
    ref_code = "direct"
    if message.text and len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
    
    # Создаем inline кнопку с TMA
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Активировать Триал",
            web_app=types.WebAppInfo(url=f"{TMA_URL}?ref={ref_code}")
        )
    ]])
    
    await message.answer(WELCOME_TEXT, reply_markup=keyboard)

# === Игнорировать всё остальное ===
@dp.message()
async def ignore_all(message: types.Message):
    pass

# === ЗАПУСК ===
async def main():
    print("Synapse Bot запущен!")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
