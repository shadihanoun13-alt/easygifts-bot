import asyncio
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    LabeledPrice, 
    PreCheckoutQuery, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

BOT_TOKEN = "8538776972:AAG-X__6ZZaf6iN7WihUB9blBRae37so0nE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USER_BALANCES = {}
USER_INVENTORIES = {}

ITEMS_POOL = [
    {"id": "bear", "name": "🧸 Teddy Bear (Common)", "weight": 55, "value": 15},
    {"id": "heart", "name": "💖 Heart Box (Rare)", "weight": 25, "value": 45},
    {"id": "trophy", "name": "🏆 Golden Trophy (Epic)", "weight": 14, "value": 120},
    {"id": "nft_star", "name": "💎 Unique Star NFT (JACKPOT)", "weight": 6, "value": 600},
]

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="🎁 Открыть кейс (50 ⭐️)")],
        [KeyboardButton(text="⭐️ Пополнить Stars"), KeyboardButton(text="🎒 Инвентарь")],
        [KeyboardButton(text="👤 Мой профиль")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def roll_lootbox():
    weights = [item["weight"] for item in ITEMS_POOL]
    return random.choices(ITEMS_POOL, weights=weights, k=1)[0]

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = 0
    if user_id not in USER_INVENTORIES:
        USER_INVENTORIES[user_id] = []
        
    await message.answer(
        f"👋 Добро пожаловать в **EasyGifts**, {message.from_user.first_name}!\n\n"
        "🎰 Испытай удачу в открытии кейсов с официальными подарками и уникальными NFT Telegram.\n\n"
        f"Твой баланс: **{USER_BALANCES[user_id]} ⭐️**\n"
        "Выбирай действие на кнопках внизу 👇",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "👤 Мой профиль")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    balance = USER_BALANCES.get(user_id, 0)
    inv_count = len(USER_INVENTORIES.get(user_id, []))
    
    await message.answer(
        f"👤 **Твой профиль:**\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"⭐️ Баланс Stars: **{balance} ⭐️**\n"
        f"🎁 Предметов в инвентаре: **{inv_count} шт.**",
        parse_mode="Markdown"
    )

@dp.message(F.text == "⭐️ Пополнить Stars")
async def buy_handler(message: types.Message):
    prices = [LabeledPrice(label="Пополнение баланса (50 Stars)", amount=50)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Пополнение баланса EasyGifts",
        description="Покупка 50 Stars для открытия лутбоксов",
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
    await message.answer(
        f"✅ Баланс успешно пополнен на **{amount} ⭐️**!\n"
        f"Текущий счёт: **{USER_BALANCES[user_id]} ⭐️**\n\n"
        "Жми «🎁 Открыть кейс», чтобы крутить!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "🎁 Открыть кейс (50 ⭐️)")
async def open_box_handler(message: types.Message):
    user_id = message.from_user.id
    balance = USER_BALANCES.get(user_id, 0)
    cost = 50

    if balance < cost:
        await message.answer(
            f"❌ **Недостаточно Stars!**\n\n"
            f"Стоимость кейса: {cost} ⭐️\n"
            f"У тебя на балансе: {balance} ⭐️\n\n"
            "Нажми кнопку **«⭐️ Пополнить Stars»** ниже.",
            parse_mode="Markdown"
        )
        return

    USER_BALANCES[user_id] -= cost
    
    msg = await message.answer("🎰 Открываем кейс... [ ▰▰▰▱▱▱▱▱ ]")
    await asyncio.sleep(0.8)
    await msg.edit_text("🎰 Открываем кейс... [ ▰▰▰▰▰▰▱▱ ]")
    await asyncio.sleep(0.8)

    drop = roll_lootbox()
    
    if user_id not in USER_INVENTORIES:
        USER_INVENTORIES[user_id] = []
    USER_INVENTORIES[user_id].append(drop)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Открыть еще раз (50 ⭐️)", callback_data="open_again")],
        [InlineKeyboardButton(text=f"💰 Продать приз за {drop['value']} ⭐️", callback_data=f"sell_last_{drop['value']}")]
    ])

    await msg.edit_text(
        f"🎉 **ТВОЙ ВЫИГРЫШ!** 🎉\n\n"
        f"Дроп: **{drop['name']}**\n"
        f"Оценочная стоимость: **{drop['value']} ⭐️**\n\n"
        f"Предмет добавлен в твой `🎒 Инвентарь`.\n"
        f"Баланс: {USER_BALANCES[user_id]} ⭐️",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "open_again")
async def cb_open_again(call: types.CallbackQuery):
    await call.answer()
    await open_box_handler(call.message)

@dp.callback_query(F.data.startswith("sell_last_"))
async def cb_sell_last(call: types.CallbackQuery):
    user_id = call.from_user.id
    val = int(call.data.split("_")[2])
    
    if USER_INVENTORIES.get(user_id):
        USER_INVENTORIES[user_id].pop()
        USER_BALANCES[user_id] = USER_BALANCES.get(user_id, 0) + val
        await call.answer("✅ Предмет продан!", show_alert=False)
        await call.message.edit_text(
            f"💰 Предмет успешно продан за **+{val} ⭐️**!\n"
            f"Текущий баланс: **{USER_BALANCES[user_id]} ⭐️**",
            parse_mode="Markdown"
        )
    else:
        await call.answer("Предмет уже продан или не найден.", show_alert=True)

@dp.message(F.text == "🎒 Инвентарь")
async def inventory_handler(message: types.Message):
    user_id = message.from_user.id
    items = USER_INVENTORIES.get(user_id, [])

    if not items:
        await message.answer("🎒 Твой инвентарь пока пуст. Открывай кейсы, чтобы выбивать подарки!")
        return

    text = "🎒 **Твой инвентарь:**\n\n"
    total_val = 0
    for idx, item in enumerate(items, 1):
        text += f"{idx}. {item['name']} — `{item['value']} ⭐️`\n"
        total_val += item["value"]

    text += f"\n📊 Всего предметов: **{len(items)}**"
    text += f"\n💎 Общая ценность: **{total_val} ⭐️**"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"♻️ Продать всё за {total_val} ⭐️", callback_data="sell_all")]
    ])

    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "sell_all")
async def cb_sell_all(call: types.CallbackQuery):
    user_id = call.from_user.id
    items = USER_INVENTORIES.get(user_id, [])
    
    if not items:
        await call.answer("Инвентарь пуст!", show_alert=True)
        return
        
    total_val = sum(item["value"] for item in items)
    USER_INVENTORIES[user_id] = []
    USER_BALANCES[user_id] = USER_BALANCES.get(user_id, 0) + total_val

    await call.answer("Все предметы проданы!", show_alert=True)
    await call.message.edit_text(
        f"♻️ Ты продал все предметы на сумму **+{total_val} ⭐️**!\n"
        f"Твой новый баланс: **{USER_BALANCES[user_id]} ⭐️**",
        parse_mode="Markdown"
    )

async def handle_ping(request):
    return web.Response(text="EasyGifts Bot is Live!")

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
