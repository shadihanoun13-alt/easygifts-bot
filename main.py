import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    WebAppInfo
)

BOT_TOKEN = "8538776972:AAG-X__6ZZaf6iN7WihUB9blBRae37so0nE"
# Твой домен на Render
WEBAPP_URL = "https://easygifts-bot.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Кнопка открытия Mini App на весь экран
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Открыть EasyGifts App", 
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Добро пожаловать в **EasyGifts** — сервис открытия кейсов с Telegram Gifts и TON.\n\n"
        "Нажимай кнопку ниже, чтобы открыть приложение 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# Раздача HTML страницы
async def handle_webapp(request):
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return web.Response(text=f.read(), content_type="text/html")
    except Exception as e:
        return web.Response(text=f"Error loading WebApp: {e}", status=500)

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_webapp)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
