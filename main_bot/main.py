from api.routers import router as fastapi_router
import logging
from main_handlers import main_handlers
from contextlib import asynccontextmanager
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramBadRequest
from databases import db
import config
from fastapi import FastAPI
import uvicorn


storage = MemoryStorage()
logging.basicConfig(filename="bot.log", level=logging.INFO)
bot: Bot = Bot(config.TOKEN)
dp = Dispatcher()
dp.include_router(main_handlers.router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url = (config.WEBHOOK_URL
                           + config.TELEGRAM_WEBHOOK_PATH))
    bot_info = await bot.get_me()
    print(f'Бот успешно запущен: {bot_info.username}')
    await db.db_start()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(fastapi_router)


@app.post(config.TELEGRAM_WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    try:
        await dp.feed_update(bot=bot, update=telegram_update)
    except TelegramBadRequest:
        pass


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=config.WEBHOOK_PORT)