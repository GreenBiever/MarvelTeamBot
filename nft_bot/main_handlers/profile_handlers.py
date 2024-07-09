import random
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, FSInputFile
from nft_bot.keyboards import kb
from nft_bot.main import translations, get_translation
from nft_bot.databases import requests
from nft_bot.states import deposit_state, withdraw_state
from nft_bot import config

bot: Bot = Bot(config.TOKEN)
router = Router()
ADMIN_ID = config.ADMIN_ID
ADMIN_ID_LIST = [int(admin_id) for admin_id in ADMIN_ID.split(",")]

"""
Callback handlers for 'PROFILE' button
"""


@router.callback_query(lambda c: c.data == "wallet")
async def wallet(call: types.CallbackQuery):
    if call.data == 'wallet':
        await call.message.delete()
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
            photo = FSInputFile(config.PHOTO_PATH)
            await bot.send_photo(call.from_user.id, photo=photo, caption=wallet_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "verification")
async def verification(call: types.CallbackQuery):
    if call.data == 'verification':
        await call.message.delete()
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_verification_kb(lang)
        verification_text = get_translation(
            lang,
            'verification_message'
        )
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=verification_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "favorites")
async def favourites(call: types.CallbackQuery):
    if call.data == 'favorites':
        await call.message.delete()
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_favourites_kb()
        favourites_text = get_translation(
            lang,
            'favourites_message'
        )
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=favourites_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "statistics")
async def statistics(call: types.CallbackQuery):
    if call.data == 'statistics':
        await call.message.delete()
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
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=statistics_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "settings")
async def settings(call: types.CallbackQuery):
    if call.data == 'settings':
        await call.message.delete()
        lang = await requests.get_user_language(call.from_user.id)
        keyboard = kb.create_settings_kb(lang)
        settings_text = get_translation(
            lang,
            'settings_message'
        )
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=settings_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "my_nft")
async def my_nft(call: types.CallbackQuery):
    if call.data == 'my_nft':
        lang = await requests.get_user_language(call.from_user.id)
        my_nft_text = get_translation(
            lang,
            'my_nft_message'
        )
        await call.answer(my_nft_text, show_alert=False)


@router.callback_query(lambda c: c.data == "how_to_create_nft")
async def how_to_create_nft(call: types.CallbackQuery):
    if call.data == 'how_to_create_nft':
        await call.message.delete()
        lang = await requests.get_user_language(call.from_user.id)
        help_text = get_translation(
            lang,
            'how_to_create_nft_message'
        )
        keyboard = kb.create_nft_kb()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, caption=help_text, photo=photo, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "back")
async def back(call: types.CallbackQuery):
    if call.data == 'back':
        await call.message.delete()
        user_id = call.from_user.id
        lang = await requests.get_user_language(user_id)
        photo = FSInputFile(config.PHOTO_PATH)
        user_info = await requests.get_user_info(user_id)
        if user_info:
            user_data, user_id, user_name, balance, currency, status, verification = user_info
            translated_status = get_translation(lang, 'statuses', status=status)
            profile_text = get_translation(
                lang,
                'profile',
                user_id=user_id,
                status=translated_status,
                balance=balance,
                currency=currency,
                verification=verification,
                ref="_"  # замените на реферальный код, если необходимо
            )
            keyboard = kb.create_profile_kb(lang)
            print('keyboard: ', keyboard)
            await bot.send_photo(user_id, photo=photo, caption=profile_text, reply_markup=keyboard)
        else:
            # Handle the case where no user is found
            await bot.send_message(user_id, text='User not found')


"""
Callback handlers for 'wallet' functionality
"""


@router.callback_query(lambda c: c.data == "top_up")
async def deposit(call: types.CallbackQuery):
    if call.data == 'top_up':
        lang = await requests.get_user_language(call.from_user.id)
        deposit_text = get_translation(
            lang,
            'deposit_message'
        )
        keyboard = kb.create_deposit_kb(lang)
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id,photo=photo, caption=deposit_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "card")
async def deposit_card(call: types.CallbackQuery, state: deposit_state.Deposit.amount):
    if call.data == 'card':
        lang = await requests.get_user_language(call.from_user.id)
        card_text = get_translation(
            lang,
            'card_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=card_text, reply_markup=kb.deposit_card_back)
        await state.set_state(deposit_state.Deposit.amount)


@router.callback_query(lambda c: c.data == "crypto")
async def deposit_crypto(call: types.CallbackQuery):
    if call.data == 'crypto':
        lang = await requests.get_user_language(call.from_user.id)
        crypto_text = get_translation(
            lang,
            'crypto_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=crypto_text, reply_markup=kb.deposit_crypto)


@router.message(StateFilter(deposit_state.Deposit.amount))
async def withdraw_amount(message: Message, state: deposit_state.Deposit.amount):
    amount = message.text
    lang = await requests.get_user_language(message.from_user.id)
    if not amount.isdigit():
        error_text = get_translation(lang,
                                     'invalid_amount_message')  # предполагаем, что есть перевод для этого сообщения
        await message.reply(error_text)
    else:
        success_text = get_translation(lang,
                                       'card_deposit_message',
                                       card_number=1234,
                                       comment='test_comment')  # предполагаем, что есть перевод для этого сообщения
        photo = FSInputFile(config.PHOTO_PATH)
        keyboard = kb.create_card_crypto_kb(lang)
        await bot.send_photo(message.from_user.id, caption=success_text, photo=photo, reply_markup=keyboard)
        await state.update_data(amount=message.text)
        await state.clear()


@router.callback_query(lambda c: c.data in ['usdt', 'btc', 'eth'])
async def choose_crypto(call: types.CallbackQuery):
    if call.data in ['usdt', 'btc', 'eth']:
        lang = await requests.get_user_language(call.from_user.id)
        crypto_text = get_translation(
            lang,
            'crypto_message',
            crypto_address=31312321312321312
        )
        photo = FSInputFile(config.PHOTO_PATH)
        keyboard = kb.create_card_crypto_kb(lang)
        await bot.send_photo(call.from_user.id, photo=photo, caption=crypto_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data in ['back_wallet', 'back_wallet2'])
async def back_to_wallet(call: types.CallbackQuery):
    if call.data == 'back_wallet':
        await call.message.delete()
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
            photo = FSInputFile(config.PHOTO_PATH)
            await bot.send_photo(call.from_user.id, photo=photo, caption=wallet_text, reply_markup=keyboard)
    elif call.data == 'back_wallet2':
        lang = await requests.get_user_language(call.from_user.id)
        deposit_text = get_translation(
            lang,
            'deposit_message'
        )
        keyboard = kb.create_deposit_kb(lang)
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=deposit_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "withdraw")
async def withdraw(call: types.CallbackQuery, state: withdraw_state.Withdraw.amount):
    if call.data == 'withdraw':
        lang = await requests.get_user_language(call.from_user.id)
        withdraw_text = get_translation(
            lang,
            'withdraw_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=withdraw_text, reply_markup=kb.withdraw)
        await state.set_state(withdraw_state.Withdraw.amount)


@router.message(StateFilter(withdraw_state.Withdraw.amount))
async def withdraw_amount(message: Message, state: withdraw_state.Withdraw.amount):
    amount = message.text
    lang = await requests.get_user_language(message.from_user.id)
    if not amount.isdigit():
        error_text = get_translation(lang,
                                     'invalid_amount_message')  # предполагаем, что есть перевод для этого сообщения
        await message.reply(error_text)
    else:
        success_text = get_translation(lang,
                                       'withdraw_success_message',
                                       amount=amount)  # предполагаем, что есть перевод для этого сообщения
        await message.answer(success_text, show_alert=False)
        await state.clear()