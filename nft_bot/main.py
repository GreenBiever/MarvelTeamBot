import asyncio, json, logging
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, FSInputFile
from aiogram import types
from keyboards import kb
from nft_bot.databases.connect import init_models
from nft_bot.databases.models import User
from nft_bot.main_handlers import profile_handlers, admin_handlers, catalog_handlers, worker_handlers
from nft_bot import config
from utils.get_exchange_rate import currency_exchange
from nft_bot.middlewares import AuthorizeMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from nft_bot.utils.main_bot_api_client import main_bot_api_client, LogRequest

form_router = Router()
storage = MemoryStorage()
logging.basicConfig(filename="bot.log", level=logging.INFO)
bot: Bot = Bot(config.TOKEN)
dp = Dispatcher()
dp.message.middleware(AuthorizeMiddleware())
dp.callback_query.middleware(AuthorizeMiddleware())

languages = ["en", "ru", "pl", "uk"]
translations = {}

for lang in languages:
    with open(f"locales/{lang}.json", "r", encoding="utf-8") as file:
        translations[lang] = json.load(file)


# Функция для получения перевода
def get_translation(lang, key, **kwargs):
    translation = translations[lang].get(key, key)
    if isinstance(translation, dict):
        translation = translation.get(kwargs['status'], kwargs['status'])
    return translation.format(**kwargs)


async def on_startup():
    await init_models()
    await currency_exchange.async_init()
    await main_bot_api_client.async_init()
    bot_info = await bot.get_me()
    print(f'Бот успешно запущен: {bot_info.username}')


async def send_profile(user: User):
    lang = user.language
    user_id = user.tg_id
    keyboard2 = kb.create_main_kb(lang)
    await bot.send_message(user_id, text='⚡️', reply_markup=keyboard2)
    if user_id in config.ADMIN_IDS:
        keyboard3 = kb.create_admin_main_kb(lang)
        await bot.send_message(user_id, text='⚡️', reply_markup=keyboard3)
    photo = FSInputFile(config.PHOTO_PATH)
    status = 'stat_blocked' if user.is_blocked else 'stat_unblocked'
    translated_status = get_translation(lang, 'statuses', status=status)

    verification = 'verify_yes' if user.is_verified else 'verify_no'
    translated_verification = get_translation(lang, 'verifications', status=verification)
    profile_text = get_translation(
        lang,
        'profile',
        user_id=user_id,
        status=translated_status,
        balance=user.balance,
        currency=user.currency.name.upper(),
        verification=translated_verification,
        ref="_"  # Replace with the referral code if necessary
    )
    keyboard = kb.create_profile_kb(lang)

    await bot.send_photo(user_id, photo=photo, caption=profile_text, reply_markup=keyboard)


async def get_greeting(message: Message, user: User, edited_message: Message = None, bot_username: str = 'test_dev_shop_bot'):
    lang = user.language
    if not edited_message:
        await bot.send_message(message.from_user.id,
                               text=f'Выберите язык:\nSelect a language:',
                               parse_mode="HTML", reply_markup=kb.language)
    else:
        await edited_message.edit_text(text=f'Выберите язык:\nSelect a language:',
                                       parse_mode="HTML", reply_markup=kb.language)


async def get_admin_greetings(message: Message, user: User, edited_message: Message = None):
    lang = user.language
    keyboard = kb.create_admin_main_kb(lang)
    if not edited_message:
        await bot.send_message(message.from_user.id,
                               text=f'Добро пожаловать, админ!',
                               parse_mode="HTML", reply_markup=keyboard)
    else:
        await edited_message.edit_text(text=f'Добро пожаловать, админ!',
                                       parse_mode="HTML", reply_markup=keyboard)


@dp.message(Command('start'))
async def cmd_start(message: Message, user: User):
    if user.referer_id is None:
        await bot.send_message(chat_id= config.TEXT_CHANNEL_ID, text='<b>Новый лохматый 🦣</b>\n\n'
                                                            f'<b>ID:</b> <code>{user.tg_id}</code>\n\n'
                                                            f'Привязывайте быстрее!', parse_mode='HTML')
    if user.tg_id in config.ADMIN_IDS:
        await get_admin_greetings(message, user)
    else:
        await get_greeting(message, user)
        if user.referer_id is not None:
            await bot.send_message(user.referer, text=f'Пользователь {user.tg_id} зарегистрировался!')




@dp.callback_query(lambda c: c.data in ['ru', 'en', 'pl', 'uk'])
async def choose_language(call: types.CallbackQuery, user: User, session: AsyncSession):
    user_id = call.from_user.id
    username = call.from_user.username
    language = call.data
    await session.execute(
        update(User)
        .where(User.tg_id == user_id)
        .values(language=language)
    )
    await session.commit()
    await send_profile(user)


async def main():
    dp.include_routers(profile_handlers.router)
    dp.include_routers(admin_handlers.router)
    dp.include_routers(catalog_handlers.router)
    dp.include_routers(worker_handlers.router)
    await dp.start_polling(bot, on_startup=await on_startup(), skip_updates=True)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
