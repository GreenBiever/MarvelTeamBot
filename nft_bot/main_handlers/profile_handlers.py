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

"""
Callback handlers for 'PROFILE' button
"""


@router.callback_query(lambda c: c.data == "wallet")
async def wallet(call: types.CallbackQuery):
    if call.data == 'wallet':
        lang = await requests.get_user_language(call.from_user.id)
        user_info = await requests.get_user_info(call.from_user.id)
        if user_info:
            user_data, user_id, user_name, balance, currency, status, _ = user_info
            wallet_text = get_translation(
                lang,
                'wallet_message',
                user_id=user_id,
                balance=balance,
                currency=currency
            )
            keyboard = kb.create_wallet_kb(lang)
            photo = FSInputFile('open_sea.jpg')
            await bot.send_photo(call.from_user.id, photo=photo, caption=wallet_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "verification")
async def verification(call: types.CallbackQuery):
    if call.data == 'verification':
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_verification_kb(lang)
        verification_text = get_translation(
            lang,
            'verification_message'
        )
        photo = FSInputFile('open_sea.jpg')
        await bot.send_photo(call.from_user.id, photo=photo, caption=verification_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "favorites")
async def favourites(call: types.CallbackQuery):
    if call.data == 'favorites':
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_favourites_kb()
        favourites_text = get_translation(
            lang,
            'favourites_message'
        )
        photo = FSInputFile('open_sea.jpg')
        await bot.send_photo(call.from_user.id, photo=photo, caption=favourites_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "statistics")
async def statistics(call: types.CallbackQuery):
    if call.data == 'statistics':
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_statistics_kb()
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


@router.callback_query(lambda c: c.data == "settings")
async def settings(call: types.CallbackQuery):
    if call.data == 'settings':
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_settings_kb(lang)
        settings_text = get_translation(
            lang,
            'settings_message'
        )
        photo = FSInputFile('open_sea.jpg')
        await bot.send_photo(call.from_user.id, photo=photo, caption=settings_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "my_nft")
async def my_nft(call: types.CallbackQuery):
    if call.data == 'my_nft':
        lang = await requests.get_user_language(call.from_user.id)
        my_nft_text = get_translation(
            lang,
            'my_nft_message'
        )
        await call.message.answer(my_nft_text, show_alert=True)


@router.callback_query(lambda c: c.data == "how_to_create_nft")
async def how_to_create_nft(call: types.CallbackQuery):
    if call.data == 'how_to_create_nft':
        lang = await requests.get_user_language(call.from_user.id)
        help_text = get_translation(
            lang,
            'how_to_create_nft_message'
        )
        keyboard = kb.create_nft_kb()
        await bot.send_message(call.from_user.id, help_text, reply_markup=keyboard)


"""
Callback handlers for 'wallet' functionality
"""


@router.callback_query(lambda c: c.data == "deposit")
async def deposit(call: types.CallbackQuery):
    if call.data == 'deposit':
        lang = await requests.get_user_language(call.from_user.id)
        deposit_text = get_translation(
            lang,
            'deposit_message'
        )
        keyboard = kb.create_deposit_kb(lang)
        await call.message.delete()
        await bot.send_message(call.from_user.id, deposit_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "withdraw")
async def withdraw(call: types.CallbackQuery):
    if call.data == 'withdraw':
        lang = await requests.get_user_language(call.from_user.id)
        withdraw_text = get_translation(
            lang,
            'withdraw_message'
        )
        await call.message.delete()
        await bot.send_message(call.from_user.id, withdraw_text, reply_markup=kb.withdraw)
