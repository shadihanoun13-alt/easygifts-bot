import asyncio
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8538776972:AAEG4cNRlDTTCO_hD7lTTABuyd8dFSMe4zo"
WEBAPP_URL = "https://easygifts-bot.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USER_BALANCES = {}
USER_INVENTORIES = {}

PRIZES = {
    "starter": [
        {"name": "Teddy Bear", "img": "https://img.icons8.com/isometric/512/teddy-bear.png", "val": 15, "weight": 60},
        {"name": "Heart Box", "img": "https://img.icons8.com/isometric/512/like.png", "val": 35, "weight": 30},
        {"name": "Diamond Ring", "img": "https://img.icons8.com/isometric/512/wedding-rings.png", "val": 100, "weight": 10},
    ],
    "rare": [
        {"name": "Diamond Ring", "img": "https://img.icons8.com/isometric/512/wedding-rings.png", "val": 100, "weight": 60},
        {"name": "Star NFT #402", "img": "https://img.icons8.com/isometric/512/star.png", "val": 450, "weight": 30},
        {"name": "TON Diamond", "img": "https://img.icons8.com/isometric/512/diamond.png", "val": 1500, "weight": 10},
    ],
    "jackpot": [
        {"name": "Star NFT #402", "img": "https://img.icons8.com/isometric/512/star.png", "val": 450, "weight": 50},
        {"name": "TON Diamond", "img": "https://img.icons8.com/isometric/512/diamond.png", "val": 1500, "weight": 40},
        {"name": "Golden Pepe NFT", "img": "https://img.icons8.com/isometric/512/frog.png", "val": 5000, "weight": 10},
    ]
}

PRICES = {"starter": 25, "rare": 75, "jackpot": 250}

# HTML закодирован в одну безопасную строку, чтобы не ломался синтаксис на телефоне
HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
body { background: #0f0a1c; color: #fff; font-family: sans-serif; margin: 0; padding: 16px; text-align: center; }
.bal { background: rgba(245,158,11,0.2); border: 1px solid #f59e0b; color: #f59e0b; padding: 8px 16px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 20px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.card { background: #1a1330; border: 1px solid rgba(168,85,247,0.3); border-radius: 16px; padding: 14px; }
.card img { width: 70px; height: 70px; }
.btn { background: #a855f7; border: none; color: #fff; padding: 10px; border-radius: 10px; width: 100%; font-weight: bold; margin-top: 8px; cursor: pointer; }
#res { margin-top: 20px; font-size: 16px; color: #4ade80; min-height: 24px; font-weight: bold; }
</style>
</head>
<body>
<div class="bal"><span id="b">...</span> ⭐️</div>
<div class="grid">
  <div class="card">
    <img src="https://img.icons8.com/isometric/512/teddy-bear.png">
    <div>Стартовый</div>
    <button class="btn" onclick="spin('starter')">25 ⭐️</button>
  </div>
  <div class="card">
    <img src="https://img.icons8.com/isometric/512/star.png">
    <div>Rare NFT</div>
    <button class="btn" onclick="spin('rare')">75 ⭐️</button>
  </div>
  <div class="card" style="grid-column: span 2;">
    <img src="https://img.icons8.com/isometric/512/frog.png">
    <div>Golden Pepe</div>
    <button class="btn" onclick="spin('jackpot')">250 ⭐️</button>
  </div>
</div>
<div id="res"></div>
<script>
const tg = window.Telegram?.WebApp;
if (tg) { tg.expand(); tg.ready(); }
const uid = tg?.initDataUnsafe?.user?.id || "demo";
async function sync() {
  const r = await fetch('/api/user?uid=' + uid);
  const d = await r.json();
  document.getElementById('b').innerText = d.balance;
}
async function spin(type) {
  document.getElementById('res').innerText = "Крутим...";
  const r = await fetch('/api/open', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ uid: uid, type: type })
  });
  const d = await r.json();
  if (!d.ok) { document.getElementById('res').innerText = d.err; return; }
  document.getElementById('b').innerText = d.balance;
  document.getElementById('res').innerText = "Выпало: " + d.item.name + " (" + d.item.val + " ⭐️)!";
}
sync();
</script>
</body>
</html>"""

@dp.message(Command("start"))
async def start_handler(msg: types.Message):
    uid = str(msg.from_user.id)
    if uid not in USER_BALANCES:
        USER_BALANCES[uid] = 250
        USER_INVENTORIES[uid] = []

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Открыть EasyGifts App", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await msg.answer(
        f"👋 Привет, {msg.from_user.first_name}!\n\n"
        f"Добро пожаловать в **EasyGifts**.\nБаланс: **{USER_BALANCES[uid]} ⭐️**",
        reply_markup=kb,
        parse_mode="Markdown"
    )

async def web_index(request):
    return web.Response(text=HTML_CONTENT, content_type="text/html")

async def web_user(request):
    uid = request.query.get("uid", "demo")
    USER_BALANCES.setdefault(uid, 250)
    return web.json_response({"balance": USER_BALANCES[uid]})

async def web_open(request):
    data = await request.json()
    uid = str(data.get("uid", "demo"))
    ctype = data.get("type", "starter")
    cost = PRICES.get(ctype, 25)
    bal = USER_BALANCES.get(uid, 250)

    if bal < cost:
        return web.json_response({"ok": False, "err": "Недостаточно Stars!"})

    USER_BALANCES[uid] = bal - cost
    pool = PRIZES.get(ctype, PRIZES["starter"])
    drop = random.choices(pool, weights=[x["weight"] for x in pool], k=1)[0]
    USER_INVENTORIES.setdefault(uid, []).append(drop)

    return web.json_response({"ok": True, "balance": USER_BALANCES[uid], "item": drop})

async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass

    app = web.Application()
    app.router.add_get("/", web_index)
    app.router.add_get("/api/user", web_user)
    app.router.add_post("/api/open", web_open)

    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
