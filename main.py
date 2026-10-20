import asyncio
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery

BOT_TOKEN = "8538776972:AAG-X__6ZZaf6iN7WihUB9blBRae37so0nE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
USER_BALANCES = {}

ITEMS_POOL = [
    {"name": "Обычный подарок (Teddy Bear)", "weight": 60, "value": 15},
    {"name": "Редкий подарок (Heart Box)", "weight": 25, "value": 50},
    {"name": "Эпический подарок (Golden Trophy)", "weight": 12, "value": 150},
    {"name": "ДЖЕКПОТ (Unique Star NFT)", "weight": 3, "value": 1000},
]

def roll_lootbox():
    weights = [item["weight"] for item in ITEMS_POOL]
    return random.choices(ITEMS_POOL, weights=weights, k=1)[0]

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = 0
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Твой баланс: {USER_BALANCES[user_id]} ⭐️\n\n"
        "Команды:\n"
        "💳 /buy — пополнить на 50 Stars\n"
        "🎁 /open — открыть кейс (стоит 50 Stars)"
    )

@dp.message(Command("buy"))
async def buy_cmd(message: types.Message):
    prices = [LabeledPrice(label="Пополнение баланса (50 Stars)", amount=50)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Пополнение баланса",
        description="Покупка 50 Stars для кейсов EasyGifts",
        payload=f"stars_deposit_{message.from_user.id}",
        currency="XTR",
        prices=prices,
        provider_token=""
    )

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(lambda msg: msg.successful_payment is not None)
async def payment_success(message: types.Message):
    user_id = message.from_user.id
    amount = message.successful_payment.total_amount
    USER_BALANCES[user_id] = USER_BALANCES.get(user_id, 0) + amount
    await message.answer(f"✅ Баланс пополнен на {amount} ⭐️! Нажми /open")

@dp.message(Command("open"))
async def open_box_cmd(message: types.Message):
    user_id = message.from_user.id
    balance = USER_BALANCES.get(user_id, 0)
    cost = 50

    if balance < cost:
        await message.answer(f"❌ Недостаточно Stars! Кейс стоит {cost} ⭐️, а у тебя {balance} ⭐️.\nНажми /buy")
        return

    USER_BALANCES[user_id] -= cost
    msg = await message.answer("🎰 Открываем кейс... [ ▰▰▰▱▱▱▱▱ ]")
    await asyncio.sleep(1)
    await msg.edit_text("🎰 Открываем кейс... [ ▰▰▰▰▰▰▱▱ ]")
    await asyncio.sleep(1)

    drop = roll_lootbox()
    await msg.edit_text(
        f"🎉 **ПОЗДРАВЛЯЕМ!** 🎉\n\n"
        f"Тебе выпало: **{drop['name']}**\n"
        f"Оценочная стоимость: **{drop['value']} ⭐️**\n\n"
        f"Остаток: {USER_BALANCES[user_id]} ⭐️\n"
        "Крути еще раз: /open"
    )

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
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
