import asyncio
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8538776972:AAEG4cNRIDTTCO_hD7lTTABuyd8dFSme4zo"
WEBAPP_URL = "https://easygifts-bot.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USER_BALANCES = {}
USER_INVENTORIES = {}
WITHDRAW_REQUESTS = []

PRIZES_POOL = {
    "starter": [
        {"id": "bear", "name": "Plush Teddy", "img": "https://img.icons8.com/isometric/512/teddy-bear.png", "type": "common", "val": 15, "weight": 60},
        {"id": "heart", "name": "Heart Box", "img": "https://img.icons8.com/isometric/512/like.png", "type": "common", "val": 35, "weight": 25},
        {"id": "ring", "name": "Diamond Ring", "img": "https://img.icons8.com/isometric/512/wedding-rings.png", "type": "rare", "val": 80, "weight": 12},
        {"id": "cup", "name": "Telegram Cup", "img": "https://img.icons8.com/isometric/512/trophy.png", "type": "rare", "val": 180, "weight": 3},
    ],
    "rare": [
        {"id": "heart", "name": "Heart Box", "img": "https://img.icons8.com/isometric/512/like.png", "type": "common", "val": 35, "weight": 45},
        {"id": "ring", "name": "Diamond Ring", "img": "https://img.icons8.com/isometric/512/wedding-rings.png", "type": "rare", "val": 80, "weight": 35},
        {"id": "star_nft", "name": "Star NFT #402", "img": "https://img.icons8.com/isometric/512/star.png", "type": "epic", "val": 400, "weight": 15},
        {"id": "dog", "name": "Spike The Dog NFT", "img": "https://img.icons8.com/isometric/512/corgi.png", "type": "legendary", "val": 1500, "weight": 5},
    ],
    "royal": [
        {"id": "ring", "name": "Diamond Ring", "img": "https://img.icons8.com/isometric/512/wedding-rings.png", "type": "rare", "val": 80, "weight": 40},
        {"id": "star_nft", "name": "Star NFT #402", "img": "https://img.icons8.com/isometric/512/star.png", "type": "epic", "val": 400, "weight": 35},
        {"id": "ton_gem", "name": "TON Crystal NFT", "img": "https://img.icons8.com/isometric/512/diamond.png", "type": "legendary", "val": 2200, "weight": 20},
        {"id": "pepe", "name": "Golden Pepe NFT", "img": "https://img.icons8.com/isometric/512/frog.png", "type": "mythic", "val": 5000, "weight": 5},
    ],
    "jackpot": [
        {"id": "star_nft", "name": "Star NFT #402", "img": "https://img.icons8.com/isometric/512/star.png", "type": "epic", "val": 400, "weight": 35},
        {"id": "dog", "name": "Spike The Dog NFT", "img": "https://img.icons8.com/isometric/512/corgi.png", "type": "legendary", "val": 1500, "weight": 35},
        {"id": "ton_gem", "name": "TON Crystal NFT", "img": "https://img.icons8.com/isometric/512/diamond.png", "type": "legendary", "val": 2200, "weight": 20},
        {"id": "pepe", "name": "Golden Pepe NFT", "img": "https://img.icons8.com/isometric/512/frog.png", "type": "mythic", "val": 5000, "weight": 10},
    ]
}

CASE_PRICES = {"starter": 25, "rare": 75, "royal": 250, "jackpot": 500}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in USER_BALANCES:
        USER_BALANCES[uid] = 250
        USER_INVENTORIES[uid] = []

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Открыть EasyGifts App", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Добро пожаловать в **EasyGifts** — кейсы с NFT и подарками Telegram.\n"
        f"Твой баланс: **{USER_BALANCES[uid]} ⭐️**\n\n"
        "Жми кнопку ниже, чтобы начать игру 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

async def handle_index(request):
    try:
        path = os.path.join(os.path.dirname(__file__), "index.html")
        with open(path, "r", encoding="utf-8") as f:
            return web.Response(text=f.read(), content_type="text/html")
    except Exception as e:
        return web.Response(text=f"index.html error: {e}", status=500)

async def api_user_data(request):
    uid = request.query.get("user_id", "demo")
    if uid not in USER_BALANCES:
        USER_BALANCES[uid] = 250
        USER_INVENTORIES[uid] = []
    return web.json_response({
        "balance": USER_BALANCES[uid],
        "inventory": USER_INVENTORIES[uid]
    })

async def api_add_balance(request):
    data = await request.json()
    uid = str(data.get("user_id", "demo"))
    amt = int(data.get("amount", 100))
    USER_BALANCES[uid] = USER_BALANCES.get(uid, 0) + amt
    return web.json_response({"ok": True, "new_balance": USER_BALANCES[uid]})

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

    item_record = {
        "id": drop["id"],
        "name": drop["name"],
        "img": drop["img"],
        "type": drop["type"],
        "val": drop["val"]
    }
    USER_INVENTORIES.setdefault(uid, []).append(item_record)

    return web.json_response({
        "ok": True,
        "new_balance": USER_BALANCES[uid],
        "drop": item_record
    })

async def api_sell_item(request):
    data = await request.json()
    uid = str(data.get("user_id", "demo"))
    idx = int(data.get("index", 0))
    items = USER_INVENTORIES.get(uid, [])

    if 0 <= idx < len(items):
        sold = items.pop(idx)
        USER_BALANCES[uid] = USER_BALANCES.get(uid, 0) + sold["val"]
        return web.json_response({"ok": True, "new_balance": USER_BALANCES[uid], "inventory": items})

    return web.json_response({"ok": False, "error": "Предмет не найден"})

async def api_withdraw_item(request):
    data = await request.json()
    uid = str(data.get("user_id", "demo"))
    idx = int(data.get("index", 0))
    target = data.get("target", "")
    items = USER_INVENTORIES.get(uid, [])

    if 0 <= idx < len(items):
        item = items.pop(idx)
        WITHDRAW_REQUESTS.append({"user_id": uid, "item": item, "target": target})
        return web.json_response({"ok": True, "inventory": items})

    return web.json_response({"ok": False, "error": "Ошибка вывода"})

async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Webhook note: {e}")

    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/user_data", api_user_data)
    app.router.add_post("/api/add_balance", api_add_balance)
    app.router.add_post("/api/open_case", api_open_case)
    app.router.add_post("/api/sell_item", api_sell_item)
    app.router.add_post("/api/withdraw_item", api_withdraw_item)

    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"EasyGifts server running on port {port}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
