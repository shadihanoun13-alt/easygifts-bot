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
  <meta charset="UTF-
