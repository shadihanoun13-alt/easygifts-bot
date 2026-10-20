import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8538776972:AAG-X__6ZZaf6iN7WihUB9blBRae37so0nE"
WEBAPP_URL = "https://easygifts-bot.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>EasyGifts</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg: #0b0717;
      --card: #150f29;
      --border: rgba(139, 92, 246, 0.2);
      --accent: #8b5cf6;
      --gold: #f59e0b;
      --cyan: #06b6d4;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-tap-highlight-color: transparent;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", Roboto, sans-serif;
    }

    body {
      background-color: var(--bg);
      background-image: 
        radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.25) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.15) 0px, transparent 50%);
      color: #fff;
      min-height: 100vh;
      padding: 16px;
      padding-bottom: 95px;
      overflow-x: hidden;
    }

    /* Верхняя панель */
    .top-nav {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
    }

    .brand-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .brand-logo {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      background: linear-gradient(135deg, #a855f7, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 17px;
      box-shadow: 0 4px 16px rgba(168, 85, 247, 0.4);
    }

    .brand-text {
      font-size: 19px;
      font-weight: 800;
      letter-spacing: -0.3px;
    }

    .stars-chip {
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.4);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 14px;
      font-weight: 800;
      color: var(--gold);
      box-shadow: 0 0 16px rgba(245, 158, 11, 0.2);
    }

    /* Баннер */
    .banner {
      background: linear-gradient(135deg, rgba(88, 28, 135, 0.4), rgba(15, 10, 30, 0.9));
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 18px;
      margin-bottom: 22px;
      position: relative;
      overflow: hidden;
    }

    .banner h2 {
      font-size: 18px;
      font-weight: 800;
      margin-bottom: 4px;
      background: linear-gradient(90deg, #fff, #c084fc);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .banner p {
      font-size: 12px;
      color: #94a3b8;
    }

    .section-head {
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #64748b;
      margin-bottom: 12px;
    }

    /* Сетка кейсов */
    .cases-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }

    .case-card {
      background: var(--card);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 22px;
      padding: 16px 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      position: relative;
      box-shadow: 0 10px 24px rgba(0,0,0,0.45);
      transition: transform 0.15s ease;
      cursor: pointer;
    }

    .case-card:active {
      transform: scale(0.96);
      border-color: var(--accent);
    }

    .case-img {
      width: 86px;
      height: 86px;
      object-fit: contain;
      margin-bottom: 10px;
      filter: drop-shadow(0 8px 18px rgba(168, 85, 247, 0.45));
    }

    .case-name {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 10px;
    }

    .btn-open {
      width: 100%;
      background: linear-gradient(135deg, #f59e0b, #d97706);
      border: none;
      border-radius: 14px;
      color: #0b0717;
      font-weight: 900;
      font-size: 14px;
      padding: 9px 0;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
    }

    /* Модалка с рулеткой */
    .modal {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.88);
      backdrop-filter: blur(14px);
      z-index: 100;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .modal-content {
      width: 100%;
      max-width: 360px;
      background: #140d28;
      border: 1px solid var(--border);
      border-radius: 26px;
      padding: 22px 16px;
      text-align: center;
      box-shadow: 0 20px 60px rgba(0,0,0,0.85);
    }

    .tape-box {
      width: 100%;
      height: 120px;
      position: relative;
      overflow: hidden;
      margin: 18px 0;
      background: rgba(0, 0, 0, 0.6);
      border-radius: 16px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .tape-pointer {
      position: absolute;
      left: 50%;
      top: 0;
      bottom: 0;
      width: 3px;
      background: #f59e0b;
      transform: translateX(-50%);
      z-index: 10;
      box-shadow: 0 0 12px #f59e0b;
    }

    .tape-track {
      display: flex;
      align-items: center;
      height: 100%;
      position: absolute;
      left: 0;
      top: 0;
      will-change: transform;
    }

    .tape-item {
      width: 90px;
      height: 90px;
      flex-shrink: 0;
      margin: 0 5px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 14px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 34px;
    }

    .tape-item.rare {
      border-color: var(--cyan);
      background: rgba(6, 182, 212, 0.12);
    }
    .tape-item.epic {
      border-color: var(--accent);
      background: rgba(139, 92, 246, 0.15);
    }
    .tape-item.legendary {
      border-color: var(--gold);
      background: rgba(245, 158, 11, 0.18);
    }

    .tape-item-title {
      font-size: 10px;
      font-weight: 700;
      margin-top: 4px;
      max-width: 80px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .modal-btn {
      width: 100%;
      background: linear-gradient(135deg, #a855f7, #7c3aed);
      border: none;
      border-radius: 14px;
      color: #fff;
      font-size: 15px;
      font-weight: 800;
      padding: 13px 0;
      cursor: pointer;
      box-shadow: 0 4px 18px rgba(168, 85, 247, 0.45);
    }

    .modal-btn-close {
      background: transparent;
      box-shadow: none;
      color: #64748b;
      margin-top: 8px;
      font-size: 13px;
    }

    /* Нижняя панель вкладок */
    .bottom-bar {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 72px;
      background: rgba(14, 9, 28, 0.92);
      backdrop-filter: blur(20px);
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      justify-content: space-around;
      align-items: center;
      z-index: 50;
      padding-bottom: 6px;
    }

    .nav-tab {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      color: #64748b;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }

    .nav-tab.active {
      color: var(--accent);
    }

    .nav-tab-icon {
      font-size: 20px;
    }
  </style>
</head>
<body>

  <!-- Верхний бар -->
  <div class="top-nav">
    <div class="brand-wrap">
      <div class="brand-logo">EG</div>
      <div class="brand-text">EasyGifts</div>
    </div>
    <div class="stars-chip">
      <span>150</span> ⭐️
    </div>
  </div>

  <!-- Главный баннер -->
  <div class="banner">
    <h2>Telegram Unique Gifts</h2>
    <p>Выбивай редкие NFT и выводи напрямую на аккаунт в Telegram</p>
  </div>

  <div class="section-head">Коллекционные кейсы</div>

  <!-- Сетка кейсов с 3D артом -->
  <div class="cases-grid">
    <div class="case-card" onclick="openRoulette('Кейс Стартовый', 25)">
      <img class="case-img" src="https://cdn-icons-png.flaticon.com/512/3209/3209955.png" alt="Box">
      <div class="case-name">Стартовый</div>
      <button class="btn-open">25 ⭐️</button>
    </div>

    <div class="case-card" onclick="openRoulette('Telegram Rare', 75)">
      <img class="case-img" src="https://cdn-icons-png.flaticon.com/512/9420/9420514.png" alt="Box">
      <div class="case-name">Telegram Rare</div>
      <button class="btn-open">75 ⭐️</button>
    </div>

    <div class="case-card" onclick="openRoulette('Royal Gold', 250)">
      <img class="case-img" src="https://cdn-icons-png.flaticon.com/512/10043/10043869.png" alt="Box">
      <div class="case-name">Royal Gold</div>
      <button class="btn-open">250 ⭐️</button>
    </div>

    <div class="case-card" onclick="openRoulette('Pepe NFT Jackpot', 500)">
      <img class="case-img" src="https://cdn-icons-png.flaticon.com/512/3132/3132693.png" alt="Box">
      <div class="case-name">Pepe Jackpot</div>
      <button class="btn-open">500 ⭐️</button>
    </div>
  </div>

  <!-- Модалка рулетки -->
  <div class="modal" id="modal">
    <div class="modal-content">
      <h3 id="modal-title" style="font-size: 17px; font-weight: 800;">Кейс</h3>
      
      <div class="tape-box">
        <div class="tape-pointer"></div>
        <div class="tape-track" id="tape-track"></div>
      </div>

      <div id="drop-result" style="min-height: 22px; font-size: 14px; font-weight: 700; margin-bottom: 12px; color: #94a3b8;">
        Испытай удачу
      </div>

      <button class="modal-btn" id="roll-btn" onclick="spinTape()">Крутить рулетку</button>
      <button class="modal-btn modal-btn-close" onclick="closeModal()">Закрыть</button>
    </div>
  </div>

  <!-- Нижний таб-бар как в Virus Game -->
  <div class="bottom-bar">
    <div class="nav-tab active">
      <div class="nav-tab-icon">🎰</div>
      <div>Кейсы</div>
    </div>
    <div class="nav-tab" onclick="alert('Инвентарь: скоро доступен прямо в WebApp!')">
      <div class="nav-tab-icon">🎒</div>
      <div>Инвентарь</div>
    </div>
    <div class="nav-tab" onclick="alert('Задания: крути кейсы и получай Stars!')">
      <div class="nav-tab-icon">📋</div>
      <div>Задания</div>
    </div>
    <div class="nav-tab" onclick="alert('Профиль: подключен аккаунт Telegram')">
      <div class="nav-tab-icon">👤</div>
      <div>Профиль</div>
    </div>
  </div>

  <script>
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.expand();
      tg.ready();
    }

    const items = [
      { name: "Teddy Bear", icon: "🧸", type: "common" },
      { name: "Heart Box", icon: "💖", type: "common" },
      { name: "Gem Ring", icon: "💍", type: "rare" },
      { name: "Golden Cup", icon: "🏆", type: "rare" },
      { name: "Star NFT", icon: "⭐", type: "epic" },
      { name: "TON Diamond", icon: "💎", type: "epic" },
      { name: "Pepe Gold", icon: "🐸", type: "legendary" }
    ];

    const track = document.getElementById('tape-track');
    const itemWidth = 100;
    let isSpinning = false;

    function openRoulette(name, price) {
      document.getElementById('modal-title').innerText = `${name} (${price} ⭐️)`;
      document.getElementById('drop-result').innerText = "Нажми кнопку для запуска";
      document.getElementById('roll-btn').style.display = "block";
      document.getElementById('modal').style.display = "flex";
      buildTape();
    }

    function closeModal() {
      if (isSpinning) return;
      document.getElementById('modal').style.display = "none";
    }

    function buildTape() {
      track.innerHTML = "";
      track.style.transition = "none";
      track.style.transform = "translateX(0px)";

      for (let i = 0; i < 50; i++) {
        const rand = items[Math.floor(Math.random() * items.length)];
        const div = document.createElement('div');
        div.className = `tape-item ${rand.type}`;
        div.innerHTML = `<span>${rand.icon}</span><span class="tape-item-title">${rand.name}</span>`;
        track.appendChild(div);
      }
    }

    function spinTape() {
      if (isSpinning) return;
      isSpinning = true;
      document.getElementById('roll-btn').style.display = "none";
      document.getElementById('drop-result').innerText = "Крутим ленту...";

      const winnerIndex = 38;
      const winner = items[Math.floor(Math.random() * items.length)];
      
      const winningNode = track.children[winnerIndex];
      winningNode.className = `tape-item ${winner.type}`;
      winningNode.innerHTML = `<span>${winner.icon}</span><span class="tape-item-title">${winner.name}</span>`;

      const wrapperWidth = document.querySelector('.tape-box').offsetWidth;
      const targetOffset = (winnerIndex * itemWidth) + (itemWidth / 2) - (wrapperWidth / 2);

      track.style.transition = "transform 4.5s cubic-bezier(0.12, 0.8, 0.32, 1)";
      track.style.transform = `translateX(-${targetOffset}px)`;

      setTimeout(() => {
        isSpinning = false;
        document.getElementById('drop-result').innerHTML = `<span style="color: #f59e0b;">Выпало: ${winner.name}!</span>`;
        if (tg && tg.HapticFeedback) {
          tg.HapticFeedback.notificationOccurred('success');
        }
      }, 4600);
    }
  </script>
</body>
</html>"""

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Открыть EasyGifts App", 
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Добро пожаловать в **EasyGifts** — сервис открытия кейсов с Telegram Gifts и TON.\n\n"
        "Жми кнопку ниже, чтобы начать игру 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

async def handle_webapp(request):
    return web.Response(text=HTML_CONTENT, content_type="text/html")

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
