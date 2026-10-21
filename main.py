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

USER_BALANCES = {}
USER_INVENTORIES = {}

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

HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>EasyGifts</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg: #090514;
      --card: #150f26;
      --border: rgba(168, 85, 247, 0.25);
      --accent: #a855f7;
      --gold: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; font-family: -apple-system, sans-serif; }
    body {
      background: var(--bg);
      background-image: radial-gradient(circle at 50% 0%, rgba(168, 85, 247, 0.22) 0%, transparent 60%);
      color: #fff; min-height: 100vh; padding: 16px 16px 85px 16px;
    }
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .brand { font-size: 18px; font-weight: 900; background: linear-gradient(90deg, #c084fc, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stars-badge { background: rgba(245, 158, 11, 0.15); border: 1px solid var(--gold); border-radius: 20px; padding: 6px 14px; font-weight: 800; color: var(--gold); font-size: 14px; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .case-card {
      background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 16px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
    }
    .case-icon { font-size: 46px; margin-bottom: 8px; }
    .case-name { font-size: 14px; font-weight: 700; margin-bottom: 10px; }
    .open-btn {
      width: 100%; background: linear-gradient(135deg, #f59e0b, #d97706); border: none; border-radius: 12px;
      padding: 10px 0; font-weight: 900; color: #000; font-size: 14px; cursor: pointer;
    }
    .modal {
      display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 100;
      flex-direction: column; align-items: center; justify-content: center; padding: 16px;
    }
    .modal-box { width: 100%; max-width: 340px; background: #130a24; border: 1px solid var(--border); border-radius: 24px; padding: 20px 16px; text-align: center; }
    .tape-box { width: 100%; height: 110px; position: relative; overflow: hidden; margin: 16px 0; background: rgba(0,0,0,0.5); border-radius: 14px; border: 1px solid rgba(255,255,255,0.08); }
    .tape-line { position: absolute; left: 50%; top: 0; bottom: 0; width: 3px; background: var(--gold); transform: translateX(-50%); z-index: 10; box-shadow: 0 0 10px var(--gold); }
    .tape-track { display: flex; align-items: center; height: 100%; position: absolute; left: 0; top: 0; }
    .tape-item { width: 80px; height: 80px; margin: 0 5px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 30px; flex-shrink: 0; }
    .spin-btn { width: 100%; background: var(--accent); border: none; border-radius: 12px; padding: 12px 0; color: #fff; font-weight: 800; font-size: 15px; cursor: pointer; }
    .close-btn { background: transparent; border: none; color: #64748b; font-size: 13px; margin-top: 10px; cursor: pointer; }
    .inv-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 16px; }
    .inv-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 10px 4px; text-align: center; }
    .inv-card span { font-size: 26px; display: block; margin-bottom: 4px; }
    .inv-card p { font-size: 10px; color: #cbd5e1; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .inv-card b { font-size: 11px; color: var(--gold); }
    .sell-btn { width: 100%; background: #10b981; border: none; border-radius: 14px; padding: 12px 0; color: #fff; font-weight: 800; font-size: 14px; cursor: pointer; }
    .nav-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 68px; background: #0e071e; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-around; align-items: center; }
    .nav-item { font-size: 11px; font-weight: 700; color: #64748b; text-align: center; cursor: pointer; }
    .nav-item span { font-size: 20px; display: block; margin-bottom: 2px; }
    .nav-item.active { color: var(--accent); }
  </style>
</head>
<body>
  <div class="top-bar">
    <div class="brand">EASYGIFTS</div>
    <div class="stars-badge"><span id="stars-val">...</span> ⭐️</div>
  </div>

  <div id="tab-cases" class="tab-content active">
    <div class="grid">
      <div class="case-card" onclick="openModal('starter', 'Стартовый', 25)">
        <div class="case-icon">📦</div>
        <div class="case-name">Стартовый</div>
        <button class="open-btn">25 ⭐️</button>
      </div>
      <div class="case-card" onclick="openModal('rare', 'Telegram Rare', 75)">
        <div class="case-icon">💎</div>
        <div class="case-name">Rare Drop</div>
        <button class="open-btn">75 ⭐️</button>
      </div>
      <div class="case-card" onclick="openModal('royal', 'Royal Gold', 250)">
        <div class="case-icon">👑</div>
        <div class="case-name">Royal Gold</div>
        <button class="open-btn">250 ⭐️</button>
      </div>
      <div class="case-card" onclick="openModal('jackpot', 'Pepe Jackpot', 500)">
        <div class="case-icon">🐸</div>
        <div class="case-name">Pepe Jackpot</div>
        <button class="open-btn">500 ⭐️</button>
      </div>
    </div>
  </div>

  <div id="tab-inv" class="tab-content">
    <div class="inv-grid" id="inv-list"></div>
    <button class="sell-btn" onclick="sellAll()">💰 Продать всё за Stars</button>
  </div>

  <div id="tab-prof" class="tab-content">
    <div class="case-card" style="text-align: left; padding: 20px;">
      <h3 id="prof-title" style="margin-bottom: 6px;">Игрок</h3>
      <p id="prof-id" style="color: #64748b; font-size: 13px;">ID: ...</p>
    </div>
  </div>

  <div class="modal" id="modal">
    <div class="modal-box">
      <h3 id="modal-title" style="margin-bottom: 4px;">Кейс</h3>
      <div class="tape-box">
        <div class="tape-line"></div>
        <div class="tape-track" id="tape-track"></div>
      </div>
      <div id="drop-status" style="font-size: 14px; font-weight: 700; color: #a1a1aa; margin-bottom: 12px; min-height: 20px;">
        Испытай удачу
      </div>
      <button class="spin-btn" id="spin-btn" onclick="startSpin()">Крутить!</button>
      <button class="close-btn" onclick="closeModal()">Закрыть</button>
    </div>
  </div>

  <div class="nav-bar">
    <div class="nav-item active" onclick="switchNav('cases', this)"><span>🎰</span>Кейсы</div>
    <div class="nav-item" onclick="switchNav('inv', this)"><span>🎒</span>Инвентарь</div>
    <div class="nav-item" onclick="switchNav('prof', this)"><span>👤</span>Профиль</div>
  </div>

  <script>
    const tg = window.Telegram?.WebApp;
    if (tg) { tg.expand(); tg.ready(); }
    const userId = tg?.initDataUnsafe?.user?.id || "demo";
    let activeCase = "starter";
    let isSpinning = false;

    if (tg?.initDataUnsafe?.user) {
      document.getElementById('prof-title').innerText = tg.initDataUnsafe.user.first_name;
      document.getElementById('prof-id').innerText = "ID: " + tg.initDataUnsafe.user.id;
    }

    async function loadData() {
      try {
        const res = await fetch(`/api/user_data?user_id=${userId}`);
        const data = await res.json();
        document.getElementById('stars-val').innerText = data.balance;
        renderInventory(data.inventory);
      } catch (e) { console.error(e); }
    }

    function switchNav(tab, el) {
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
      document.getElementById('tab-' + tab).classList.add('active');
      el.classList.add('active');
      if (tab === 'inv') loadData();
    }

    function renderInventory(items) {
      const box = document.getElementById('inv-list');
      box.innerHTML = '';
      if (!items || items.length === 0) {
        box.innerHTML = '<div style="grid-column: 1/-1; color: #64748b; padding: 30px 0; text-align: center;">Инвентарь пуст</div>';
        return;
      }
      items.forEach(i => {
        const d = document.createElement('div');
        d.className = 'inv-card';
        d.innerHTML = `<span>${i.icon}</span><p>${i.name}</p><b>${i.val} ⭐️</b>`;
        box.appendChild(d);
      });
    }

    async function sellAll() {
      const res = await fetch('/api/sell_all', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: userId })
      });
      const data = await res.json();
      if (data.ok) {
        document.getElementById('stars-val').innerText = data.new_balance;
        renderInventory([]);
        if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
      }
    }

    function openModal(type, title, price) {
      activeCase = type;
      document.getElementById('modal-title').innerText = `${title} (${price} ⭐️)`;
      document.getElementById('drop-status').innerText = "Нажми кнопку, чтобы открыть";
      document.getElementById('spin-btn').style.display = "block";
      document.getElementById('modal').style.display = "flex";
      buildTrack();
    }

    function closeModal() {
      if (isSpinning) return;
      document.getElementById('modal').style.display = "none";
    }

    function buildTrack() {
      const track = document.getElementById('tape-track');
      track.style.transition = "none";
      track.style.transform = "translateX(0px)";
      track.innerHTML = "";
      const icons = ["🧸", "💖", "💍", "🏆", "⭐", "💎", "🐸"];
      for (let i = 0; i < 45; i++) {
        const item = document.createElement('div');
        item.className = "tape-item";
        item.innerText = icons[Math.floor(Math.random() * icons.length)];
        track.appendChild(item);
      }
    }

    async function startSpin() {
      if (isSpinning) return;
      const btn = document.getElementById('spin-btn');
      const status = document.getElementById('drop-status');
      btn.style.display = "none";
      status.innerText = "Связь с сервером...";

      try {
        const res = await fetch('/api/open_case', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ user_id: userId, case_type: activeCase })
        });
        const data = await res.json();

        if (!data.ok) {
          status.innerText = data.error;
          btn.style.display = "block";
          return;
        }

        document.getElementById('stars-val').innerText = data.new_balance;
        isSpinning = true;
        status.innerText = "Крутим ленту...";

        const track = document.getElementById('tape-track');
        track.children[35].innerText = data.drop.icon;

        const targetOffset = (35 * 90) + 45 - (document.querySelector('.tape-box').offsetWidth / 2);
        track.style.transition = "transform 4.5s cubic-bezier(0.12, 0.8, 0.32, 1)";
        track.style.transform = `translateX(-${targetOffset}px)`;

        setTimeout(() => {
          isSpinning = false;
          status.innerHTML = `<span style="color: #f59e0b;">Выпало: ${data.drop.name}!</span>`;
          if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
        }, 4600);

      } catch (err) {
        status.innerText = "Ошибка сети";
        btn.style.display = "block";
      }
    }

    loadData();
  </script>
</body>
</html>"""

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
        f"Добро пожаловать в **EasyGifts**.\n"
        f"Твой баланс: **{USER_BALANCES[uid]} ⭐️**\n\n"
        "Нажимай кнопку ниже, чтобы запустить игру 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

async def handle_index(request):
    return web.Response(text=HTML_PAGE, content_type="text/html")

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

async def main():
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/user_data", api_user_data)
    app.router.add_post("/api/open_case", api_open_case)
    app.router.add_post("/api/sell_all", api_sell_all)

    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Server started on port {port}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
