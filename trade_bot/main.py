from aiogram import Bot, Dispatcher
import config
import asyncio
from handlers import main_handlers, wallet_handlers
from database.connect import init_models, dispose_engine
import logging


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher()
dp.include_routers(main_handlers.router, wallet_handlers.router)

async def main():
    await init_models()
    await dp.start_polling(bot)
    await dispose_engine()

if __name__ == '__main__':
    asyncio.run(main())