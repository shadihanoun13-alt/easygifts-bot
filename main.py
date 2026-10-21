import asyncio
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8538776972:AAG-X__6ZZaf6iN7WihUB9blBRae37so0nE"
WEBAPP_URL = "https://easygifts-bot.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временная база данных в памяти
USER_BALANCES = {}
USER_INVENTORIES = {}

# Каталог призов
PRIZES_POOL = {
    "starter": [
        {"name": "Teddy Bear", "icon": "🧸", "rarity": "common", "val": 15, "weight": 60},
        {"name": "Heart Box", "icon": "💖", "rarity": "common", "val": 35, "weight": 25},
        {"name": "Gem Ring", "icon": "💍", "rarity": "rare", "val": 80, "weight": 12},
        {"name": "Golden Cup", "icon": "🏆", "rarity": "epic", "val": 200, "weight": 3},
    ],
    "rare": [
        {"name": "Heart Box", "icon": "💖", "rarity": "common", "val": 35, "weight": 50},
        {"name": "Gem Ring", "icon": "💍", "rarity": "rare", "val": 80, "weight": 30},
        {"name": "Golden Cup", "icon": "🏆", "rarity": "epic", "val": 200, "weight": 15},
        {"name": "Star NFT", "icon": "⭐", "rarity": "epic", "val": 450, "weight": 5},
    ],
    "royal": [
        {"name": "Gem Ring", "icon": "💍", "rarity": "rare", "val": 80, "weight": 45},
        {"name": "Golden Cup", "icon": "🏆", "rarity": "epic", "val": 200, "weight": 35},
        {"name": "Star NFT", "icon": "⭐", "rarity": "epic", "val": 450, "weight": 15},
        {"name": "TON Diamond", "icon": "💎", "rarity": "legendary", "val": 1200, "weight": 5},
    ],
    "jackpot": [
        {"name": "Golden Cup", "icon": "🏆", "rarity": "epic", "val": 200, "weight": 40},
        {"name": "Star NFT", "icon": "⭐", "rarity": "epic", "val": 450, "weight": 35},
        {"name": "TON Diamond", "icon": "💎", "rarity": "legendary", "val": 1200, "weight": 20},
        {"name": "Pepe Gold", "icon": "🐸", "rarity": "legendary", "val": 3000, "weight": 5},
    ]
}

CASE_PRICES = {"starter": 25, "rare": 75, "royal": 250, "jackpot": 500}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in USER_BALANCES:
        USER_BALANCES[uid] = 250  # Стартовый бонус для тестов
        USER_INVENTORIES[uid] = []

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Открыть EasyGifts App", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Добро пожаловать в **EasyGifts**.\n"
        f"Твой баланс: **{USER_BALANCES[uid]} ⭐️**\n\n"
        "Нажимай кнопку ниже, чтобы запустить лутку 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# --- HTTP API для Mini App ---

async def handle_index(request):
    try:
        path = os.path.join(os.path.dirname(__file__), "index.html")
        with open(path, "r", encoding="utf-8") as f:
            return web.Response(text=f.read(), content_type="text/html")
    except Exception as e:
        return web.Response(text=f"Error reading index.html: {e}", status=500)

async def api_user_data(request):
    uid = request.query.get("user_id", "demo")
    if uid not in USER_BALANCES:
        USER_BALANCES[uid] = 250
        USER_INVENTORIES[uid] = []
    
    return web.json_response({
        "balance": USER_BALANCES[uid],
        "inventory": USER_INVENTORIES[uid]
    })

async def api_open_case(request):
    data = await request.json()
    uid = str(data.get("user_id", "demo"))
    case_type = data.get("case_type", "starter")

    cost = CASE_PRICES.get(case_type, 25)
    balance = USER_BALANCES.get(uid, 250)

    if balance < cost:
        return web.json_response({"ok": False, "error": "Недостаточно Stars!"})

    USER_BALANCES[uid] = balance - cost

    pool = PRIZES_POOL.get(case_type, PRIZES_POOL["starter"])
    weights = [i["weight"] for i in pool]
    drop = random.choices(pool, weights=weights, k=1)[0]

    # Сохраняем в инвентарь (без веса)
    item_record = {
        "name": drop["name"],
        "icon": drop["icon"],
        "rarity": drop["rarity"],
        "val": drop["val"]
    }
    USER_INVENTORIES.setdefault(uid, []).append(item_record)

    return web.json_response({
        "ok": True,
        "new_balance": USER_BALANCES[uid],
        "drop": item_record
    })

async def api_sell_all(request):
    data = await request.json()
    uid = str(data.get("user_id", "demo"))
    
    items = USER_INVENTORIES.get(uid, [])
    if not items:
        return web.json_response({"ok": False, "error": "Инвентарь пуст"})

    total = sum(i["val"] for i in items)
    USER_BALANCES[uid] = USER_BALANCES.get(uid, 0) + total
    USER_INVENTORIES[uid] = []

    return web.json_response({
        "ok": True,
        "new_balance": USER_BALANCES[uid],
        "gained": total
    })

async def start_web_server():
    app = web.Application()
    app.router.add_
