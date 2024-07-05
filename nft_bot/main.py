import asyncio
import json
import logging
import os
import random
from aiogram.filters import StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, F, Router
from databases import requests, models
import config
from aiogram.types import Message, FSInputFile
from aiogram import types
from keyboards import kb
from states import application_state
from main_handlers import profile_handlers

form_router = Router()
storage = MemoryStorage()
logging.basicConfig(filename="bot.log", level=logging.INFO)
bot: Bot = Bot(config.TOKEN)
dp = Dispatcher()

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
    bot_info = await bot.get_me()
    print(f'Бот успешно запущен: {bot_info.username}')


async def send_profile(user_id):
    await bot.send_message(user_id, text='⚡️')
    lang = await requests.get_user_language(user_id)
    photo = FSInputFile('open_sea.jpg')
    user_info = await requests.get_user_info(user_id)
    if user_info:
        user_data, user_id, user_name, balance, status, verification = user_info
        translated_status = get_translation(lang, 'statuses', status=status)
        profile_text = get_translation(
            lang,
            'profile',
            user_id=user_id,
            status=translated_status,
            balance=balance,
            verification=verification,
            ref="_"  # замените на реферальный код, если необходимо
        )
        keyboard = kb.create_profile_kb(lang)
        await bot.send_photo(user_id, photo=photo, caption=profile_text, reply_markup=keyboard)
    else:
        # Handle the case where no user is found
        await bot.send_message(user_id, text='User not found')



@dp.message(F.text == '/start')
async def cmd_start(message: Message):
    user = await requests.get_user_info(message.from_user.id)
    if user:
        ADMIN_ID = config.ADMIN_ID
        ADMIN_ID_LIST = [int(admin_id) for admin_id in ADMIN_ID.split(",")]
        status = await requests.get_user_status(message.from_user.id)
        lang = await requests.get_user_language(message.from_user.id)
        if status == "blocked":
            await message.answer(get_translation(lang, 'blocked'))
        else:
            await send_profile(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id,
                               text=f'Выберите язык:\nSelect a language:',
                               parse_mode="HTML", reply_markup=kb.language)


@dp.callback_query(lambda c: c.data in ['ru', 'en', 'pl', 'uk'])
async def choose_language(call: types.CallbackQuery):
    user_id = call.from_user.id
    username = call.from_user.username
    language = call.data
    await requests.add_user(user_id, username, language)
    await send_profile(user_id)


async def main():
    await models.async_main()
    dp.include_routers(profile_handlers.router)
    await dp.start_polling(bot, on_startup=await on_startup(), skip_updates=True)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
