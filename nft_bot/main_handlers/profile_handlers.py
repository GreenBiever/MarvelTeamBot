import nft_bot.config
from nft_bot.databases import db
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import Message
from nft_bot.keyboards import kb

bot: Bot = Bot(nft_bot.config.TOKEN)
router = Router()
ADMIN_ID = nft_bot.config.ADMIN_ID
ADMIN_ID_LIST = [int(admin_id) for admin_id in ADMIN_ID.split(",")]
