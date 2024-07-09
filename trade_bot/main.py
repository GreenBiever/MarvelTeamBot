from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramBadRequest
import config
from handlers import main_handlers, wallet_handlers
from database.connect import init_models, dispose_engine
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from site_backend import routers as api_router
import uvicorn


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher()
dp.include_routers(main_handlers.router, 
                   wallet_handlers.router
                   )

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url = (config.WEBHOOK_URL
                           + config.TELEGRAM_WEBHOOK_PATH))
    bot_info = await bot.get_me()
    logging.getLogger(__name__).info(f'Бот успешно запущен: {bot_info.username}')
    await init_models()
    yield
    await bot.delete_webhook()
    await bot.close()
    await dispose_engine()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router.router)
app.mount("/exchange", StaticFiles(directory="okx/ru/exchange"), name="static")


@app.post(config.TELEGRAM_WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    try:
        await dp.feed_update(bot=bot, update=telegram_update)
    except TelegramBadRequest as e:
        logging.error(e, stack_info=True)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=config.WEBHOOK_PORT)