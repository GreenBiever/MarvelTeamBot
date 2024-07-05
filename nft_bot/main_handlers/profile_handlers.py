import random

import nft_bot.config
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import Message, FSInputFile
from nft_bot.keyboards import kb
from nft_bot.main import translations, get_translation
from nft_bot.databases import requests

bot: Bot = Bot(nft_bot.config.TOKEN)
router = Router()
ADMIN_ID = nft_bot.config.ADMIN_ID
ADMIN_ID_LIST = [int(admin_id) for admin_id in ADMIN_ID.split(",")]


@router.callback_query(lambda c: c.data == "wallet")
async def wallet(call: types.CallbackQuery):
    if call == 'wallet':
        lang = await requests.get_user_language(call.from_user.id)
        user_info = await requests.get_user_info(call.from_user.id)
        if user_info:
            user_data, user_id, user_name, balance, status, _ = user_info
            wallet_text = get_translation(
                lang,
                'wallet_message',
                user_id=user_id,
                balance=balance
            )
            keyboard = kb.create_wallet_kb(lang)
            photo = FSInputFile('open_sea.jpg')
            await bot.send_photo(call.from_user.id, photo=photo, caption=wallet_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "verification")
async def verification(call: types.CallbackQuery):
    if call == 'verification':
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_verification_kb(lang)
        verification_text = get_translation(
            lang,
            'verification_message'
        )
        photo = FSInputFile('open_sea.jpg')
        await bot.send_photo(call.from_user.id, photo=photo, caption=verification_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "favourites")
async def favourites(call: types.CallbackQuery):
    if call == 'favourites':
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_favourites_kb(lang)
        favourites_text = get_translation(
            lang,
            'favourites_message'
        )
        photo = FSInputFile('open_sea.jpg')
        await bot.send_photo(call.from_user.id, photo=photo, caption=favourites_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "statistics")
async def statistics(call: types.CallbackQuery):
    if call == 'statistics':
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_favourites_kb(lang)
        no_orders = random.randint(30, 150)
        no_online = random.randint(450, 550)
        no_views = random.randint(350, 500)
        big_deal = random.randint(250, 1000)

        statistics_text = get_translation(
            lang,
            'statistics_message',
            no_orders=no_orders,
            no_online=no_online,
            no_views=no_views,
            big_deal=big_deal
        )
        photo = FSInputFile('open_sea.jpg')
        await bot.send_photo(call.from_user.id, photo=photo, caption=statistics_text, reply_markup=keyboard)
