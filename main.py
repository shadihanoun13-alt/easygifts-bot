import asyncio
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8538776972:AAEG4cNRlDTTCO_hD7lTTabuyd8dFSMe4zo"
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

HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>EasyGifts</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg: #0b0718;
      --card: #150f28;
      --border: rgba(147, 51, 234, 0.25);
      --accent: #a855f7;
      --gold: #f59e0b;
      --cyan: #06b6d4;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; font-family: -apple-system, sans-serif; }
    body {
      background: var(--bg);
      background-image: radial-gradient(circle at 50% 0%, rgba(168, 85, 247, 0.22) 0%, transparent 60%);
      color: #fff; min-height: 100vh; padding: 16px 16px 90px 16px;
    }
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .brand { font-size: 19px; font-weight: 900; background: linear-gradient(90deg, #c084fc, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stars-badge { background: rgba(245, 158, 11, 0.15); border: 1px solid var(--gold); border-radius: 20px; padding: 7px 16px; font-weight: 800; color: var(--gold); font-size: 14px; cursor: pointer; }
    
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .case-card {
      background: var(--card); border: 1px solid var(--border); border-radius: 22px; padding: 16px 12px;
      display: flex; flex-direction: column; align-items: center; text-align: center; cursor: pointer;
    }
    .case-art { width: 84px; height: 84px; object-fit: contain; margin-bottom: 8px; filter: drop-shadow(0 6px 14px rgba(168, 85, 247, 0.45)); }
    .case-name { font-size: 14px; font-weight: 800; margin-bottom: 10px; }
    .open-btn {
      width: 100%; background: linear-gradient(135deg, #f59e0b, #d97706); border: none; border-radius: 12px;
      padding: 10px 0; font-weight: 900; color: #0b0718; font-size: 14px; cursor: pointer;
    }

    .modal {
      display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.92); z-index: 100;
      flex-direction: column; align-items: center; justify-content: center; padding: 16px;
    }
    .modal-box { width: 100%; max-width: 340px; background: #130a24; border: 1px solid var(--border); border-radius: 24px; padding: 20px 16px; text-align: center; }
    .tape-box { width: 100%; height: 110px; position: relative; overflow: hidden; margin: 16px 0; background: rgba(0,0,0,0.6); border-radius: 14px; border: 1px solid rgba(255,255,255,0.08); }
    .tape-line { position: absolute; left: 50%; top: 0; bottom: 0; width: 3px; background: var(--gold); transform: translateX(-50%); z-index: 10; box-shadow: 0 0 10px var(--gold); }
    .tape-track { display: flex; align-items: center; height: 100%; position: absolute; left: 0; top: 0; }
    .tape-item { width: 80px; height: 80px; margin: 0 5px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .tape-item img { width: 55px; height: 55px; object-fit: contain; }
    .spin-btn { width: 100%; background: var(--accent); border: none; border-radius: 12px; padding: 12px 0; color: #fff; font-weight: 800; font-size: 15px; cursor: pointer; }
    .close-btn { background: transparent; border: none; color: #64748b; font-size: 13px; margin-top: 10px; cursor: pointer; }

    .inv-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }
    .inv-card { background: var(--card); border: 1px solid var(--border); border-radius: 18px; padding: 14px 10px; text-align: center; }
    .inv-card img { width: 60px; height: 60px; object-fit: contain; margin-bottom: 6px; }
    .inv-card h4 { font-size: 12px; font-weight: 800; margin-bottom: 4px; }
    .inv-card p { font-size: 12px; color: var(--gold); font-weight: 800; margin-bottom: 10px; }
    .inv-actions { display: flex; gap: 6px; }
    .inv-btn-sell { flex: 1; background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #10b981; border-radius: 8px; font-size: 10px; font-weight: 800; padding: 6px 0; cursor: pointer; }
    .inv-btn-withdraw { flex: 1; background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; color: #3b82f6; border-radius: 8px; font-size: 10px; font-weight: 800; padding: 6px 0; cursor: pointer; }

    .deposit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 16px 0; }
    .deposit-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 14px; text-align: center; cursor: pointer; }
    .deposit-card b { display: block; font-size: 16px; color: var(--gold); }
    .deposit-card span { font-size: 11px; color: #94a3b8; }

    .nav-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 68px; background: #0e071e; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-around; align-items: center; z-index: 50; }
    .nav-item { font-size: 11px; font-weight: 700; color: #64748b; text-align: center; cursor: pointer; }
    .nav-item span { font-size: 20px; display: block; margin-bottom: 2px; }
    .nav-item.active { color: var(--accent); }
  </style>
</head>
<body>

  <div class="top-bar">
    <div class="brand">EASYGIFTS</div>
    <div class="stars-badge" onclick="openDepositModal()"><span id="stars-val">...</span> ⭐️ ＋</div>
  </div>

  <div id="tab-cases" class="tab-content active">
    <div class="grid">
      <div class="case-card" onclick="openModal('starter', 'Стартовый', 25)">
        <img class="case-art" src="https://img.icons8.com/isometric/512/teddy-bear.png">
        <div class="case-name">Стартовый</div>
        <button class="open-btn">25 ⭐️</button>
      </div>
      <div class="case-card" onclick="openModal('rare', 'Telegram Rare', 75)">
        <img class="case-art" src="https://img.icons8.com/isometric/512/star.png">
        <div class="case-name">Rare NFT Drop</div>
        <button class="open-btn">75 ⭐️</button>
      </div>
      <div class="case-card" onclick="openModal('royal', 'Royal Gold', 250)">
        <img class="case-art" src="https://img.icons8.com/isometric/512/diamond.png">
        <div class="case-name">TON Crystal</div>
        <button class="open-btn">250 ⭐️</button>
      </div>
      <div class="case-card" onclick="openModal('jackpot', 'Pepe Jackpot', 500)">
        <img class="case-art" src="https://img.icons8.com/isometric/512/frog.png">
        <div class="case-name">Pepe Jackpot</div>
        <button class="open-btn">500 ⭐️</button>
      </div>
    </div>
  </div>

  <div id="tab-inv" class="tab-content">
    <div class="inv-grid" id="inv-list"></div>
  </div>

  <div id="tab-prof" class="tab-content">
    <div class="case-card" style="text-align: left; padding: 20px;">
      <h3 id="prof-title" style="margin-bottom: 6px;">Игрок</h3>
      <p id="prof-id" style="color: #64748b; font-size: 13px; margin-bottom: 14px;">ID: ...</p>
      <button class="open-btn" onclick="openDepositModal()">⭐️ Пополнить счёт Stars</button>
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

  <div class="modal" id="deposit-modal">
    <div class="modal-box">
      <h3>Пополнить Stars ⭐️</h3>
      <p style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Выберите сумму для пополнения</p>
      <div class="deposit-grid">
        <div class="deposit-card" onclick="buyStars(50)">
          <b>50 ⭐️</b>
          <span>Тестовый</span>
        </div>
        <div class="deposit-card" onclick="buyStars(100)">
          <b>100 ⭐️</b>
          <span>Популярный</span>
        </div>
        <div class="deposit-card" onclick="buyStars(250)">
          <b>250 ⭐️</b>
          <span>Выгодный</span>
        </div>
        <div class="deposit-card" onclick="buyStars(500)">
          <b>500 ⭐️</b>
          <span>VIP Пакет</span>
        </div>
      </div>
      <button class="close-btn" onclick="closeDepositModal()">Отмена</button>
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
        box.innerHTML = '<div style="grid-column: 1/-1; color: #64748b; padding: 40px 0; text-align: center;">Инвентарь пуст.<br>Открывай кейсы!</div>';
        return;
      }
      items.forEach((item, index) => {
        const d = document.createElement('div');
        d.className = 'inv-card';
        d.innerHTML = `
          <img src="${item.img}">
          <h4>${item.name}</h4>
          <p>${item.val} ⭐️</p>
          <div class="inv-actions">
            <button class="inv-btn-sell" onclick="sellItem(${index})">Продать</button>
            <button class="inv-btn-withdraw" onclick="withdrawItem(${index}, '${item.name}')">Вывести</button>
          </div>
        `;
        box.appendChild(d);
      });
    }

    async function sellItem(idx) {
      const res = await fetch('/api/sell_item', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: userId, index: idx })
      });
      const data = await res.json();
      if (data.ok) {
        document.getElementById('stars-val').innerText = data.new_balance;
        renderInventory(data.inventory);
        if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
      }
    }

    async function withdrawItem(idx, name) {
      const address = prompt(`Куда вывести ${name}? Укажите @username или TON-кошелек:`);
      if (!address) return;

      const res = await fetch('/api/withdraw_item', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: userId, index: idx, target: address })
      });
      const data = await res.json();
      if (data.ok) {
        alert("Заявка на вывод создана! Скоро появится в профиле.");
        renderInventory(data.inventory);
      }
    }

    function openDepositModal() { document.getElementById('deposit-modal').style.display = 'flex'; }
    function closeDepositModal() { document.getElementById('deposit-modal').style.display = 'none'; }

    async function buyStars(amount) {
      const res = await fetch('/api/add_balance', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: userId, amount: amount })
      });
      const data = await res.json();
      if (data.ok) {
        document.getElementById('stars-val').innerText = data.new_balance;
        closeDepositModal();
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

    const defaultPool = [
      "https://img.icons8.com/isometric/512/teddy-bear.png",
      "https://img.icons8.com/isometric/512/like.png",
      "https://img.icons8.com/isometric/512/wedding-rings.png",
      "https://img.icons8.com/isometric/512/trophy.png",
      "https://img.icons8.com/isometric/512/star.png",
      "https://img.icons8.com/isometric/512/diamond.png",
      "https://img.icons8.com/isometric/512/frog.png"
    ];

    function buildTrack() {
      const track = document.getElementById('tape-track');
      track.style.transition = "none";
      track.style.transform = "translateX(0px)";
      track.innerHTML = "";
      for (let i = 0; i < 45; i++) {
        const item = document.createElement('div');
        item.className = "tape-item";
        item.innerHTML = `<img src="${defaultPool[Math.floor(Math.random() * defaultPool.length)]}">`;
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
        track.children[35].innerHTML = `<img src="${data.drop.img}">`;

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
        f"Добро пожаловать в **EasyGifts** — открытие кейсов с NFT и подарками Telegram.\n"
        f"Твой баланс: **{USER_BALANCES[uid]} ⭐️**\n\n"
        "Жми кнопку ниже, чтобы начать 👇",
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
        print(f"WITHDRAW REQUEST: User {uid} -> {item['name']} to {target}")
        return web.json_response({"ok": True, "inventory": items})

    return web.json_response({"ok": False, "error": "Ошибка вывода"})

async def main():
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
    print(f"EasyGifts running on port {port}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
