import random
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, FSInputFile
from nft_bot.keyboards import kb
from nft_bot.main import translations, get_translation, send_profile
from nft_bot.databases import requests
from nft_bot.states import deposit_state, withdraw_state
from nft_bot import config
from nft_bot.databases.models import User
from nft_bot.middlewares import AuthorizeMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from nft_bot.databases.enums import CurrencyEnum

bot: Bot = Bot(config.TOKEN)
router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())

ADMIN_ID = config.ADMIN_ID
ADMIN_ID_LIST = [int(admin_id) for admin_id in ADMIN_ID.split(",")]

"""
Callback handlers for 'PROFILE' button
"""


@router.message(F.text == "💼 Личный кабинет")
async def profile(message: Message, user: User):
    await send_profile(user)


@router.callback_query(lambda c: c.data == "wallet")
async def wallet(call: types.CallbackQuery, user: User):
    if call.data == 'wallet':
        await call.message.delete()
        lang = user.language
        wallet_text = get_translation(
            lang,
            'wallet_message',
            user_id=user.tg_id,
            balance=user.balance,
            currency=user.currency.name.upper()
        )
        keyboard = kb.create_wallet_kb(lang)
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=wallet_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "verification")
async def verification(call: types.CallbackQuery, user: User):
    if call.data == 'verification':
        await call.message.delete()
        lang = user.language
        keyboard = kb.create_verification_kb(lang)
        verification_text = get_translation(
            lang,
            'verification_message'
        )
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=verification_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "favorites")
async def favourites(call: types.CallbackQuery, user: User):
    if call.data == 'favorites':
        await call.message.delete()
        lang = user.language
        keyboard = kb.create_favourites_kb()
        favourites_text = get_translation(
            lang,
            'favourites_message'
        )
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=favourites_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "statistics")
async def statistics(call: types.CallbackQuery, user: User):
    if call.data == 'statistics':
        await call.message.delete()
        lang = user.language
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
async def settings(call: types.CallbackQuery, user: User):
    if call.data == 'settings':
        await call.message.delete()
        lang = user.language
        keyboard = kb.create_settings_kb(lang)
        settings_text = get_translation(
            lang,
            'settings_message'
        )
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=settings_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "my_nft")
async def my_nft(call: types.CallbackQuery,  user: User):
    if call.data == 'my_nft':
        lang = user.language
        my_nft_text = get_translation(
            lang,
            'my_nft_message'
        )
        await call.answer(my_nft_text, show_alert=False)


@router.callback_query(lambda c: c.data == "how_to_create_nft")
async def how_to_create_nft(call: types.CallbackQuery, user: User):
    if call.data == 'how_to_create_nft':
        await call.message.delete()
        lang = user.language
        help_text = get_translation(
            lang,
            'how_to_create_nft_message'
        )
        keyboard = kb.create_nft_kb()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, caption=help_text, photo=photo, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "back")
async def back(call: types.CallbackQuery, user: User):
    if call.data == 'back':
        await call.message.delete()
        await send_profile(user)


"""
Callback handlers for 'wallet' functionality
"""


@router.callback_query(lambda c: c.data == "top_up")
async def deposit(call: types.CallbackQuery, user: User):
    if call.data == 'top_up':
        lang = user.language
        deposit_text = get_translation(
            lang,
            'deposit_message'
        )
        keyboard = kb.create_deposit_kb(lang)
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=deposit_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "card")
async def deposit_card(call: types.CallbackQuery, state: deposit_state.Deposit.amount, user: User):
    if call.data == 'card':
        lang = user.language
        card_text = get_translation(
            lang,
            'card_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=card_text, reply_markup=kb.deposit_card_back)
        await state.set_state(deposit_state.Deposit.amount)


@router.callback_query(lambda c: c.data == "crypto")
async def deposit_crypto(call: types.CallbackQuery, user: User):
    if call.data == 'crypto':
        lang = user.language
        crypto_text = get_translation(
            lang,
            'crypto_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=crypto_text, reply_markup=kb.deposit_crypto)


@router.message(StateFilter(deposit_state.Deposit.amount))
async def withdraw_amount(message: Message, state: deposit_state.Deposit.amount, user: User):
    amount = message.text
    lang = user.language
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
async def choose_crypto(call: types.CallbackQuery, user: User):
    if call.data in ['usdt', 'btc', 'eth']:
        lang = user.language
        crypto_text = get_translation(
            lang,
            'crypto_message',
            crypto_address=31312321312321312
        )
        photo = FSInputFile(config.PHOTO_PATH)
        keyboard = kb.create_card_crypto_kb(lang)
        await bot.send_photo(call.from_user.id, photo=photo, caption=crypto_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data in ['back_wallet', 'back_wallet2'])
async def back_to_wallet(call: types.CallbackQuery, state: deposit_state.Deposit.amount, user: User):
    if call.data == 'back_wallet':
        await state.clear()
        await call.message.delete()
        lang = user.language
        wallet_text = get_translation(
            lang,
            'wallet_message',
            user_id=user.tg_id,
            balance=user.balance,
            currency=user.currency.name.upper()
        )
        keyboard = kb.create_wallet_kb(lang)
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=wallet_text, reply_markup=keyboard)
    elif call.data == 'back_wallet2':
        await state.clear()
        lang = user.language
        deposit_text = get_translation(
            lang,
            'deposit_message'
        )
        keyboard = kb.create_deposit_kb(lang)
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=deposit_text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "withdraw")
async def withdraw(call: types.CallbackQuery, state: withdraw_state.Withdraw.amount, user: User):
    if call.data == 'withdraw':
        lang = user.language
        withdraw_text = get_translation(
            lang,
            'withdraw_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=withdraw_text, reply_markup=kb.withdraw)
        await state.set_state(withdraw_state.Withdraw.amount)


@router.message(StateFilter(withdraw_state.Withdraw.amount))
async def withdraw_amount(message: Message, state: withdraw_state.Withdraw.amount, user: User):
    amount = message.text
    lang = user.language
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


@router.callback_query(lambda c: c.data == "promocode")
async def promocode(call: types.CallbackQuery, state: deposit_state.Promocode.promo, user: User):
    if call.data == 'promocode':
        lang = user.language
        promocode_text = get_translation(
            lang,
            'promocode_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=promocode_text, reply_markup=kb.withdraw)
        await state.set_state(deposit_state.Promocode.promo)


@router.message(StateFilter(deposit_state.Promocode.promo))
async def promocode_message(message: Message, state: deposit_state.Promocode.promo, user: User):
    promo = message.text
    lang = user.language
    success_text = get_translation(lang,
                                   'promocode_success_message',
                                   promo=promo)  # предполагаем, что есть перевод для этого сообщения
    await bot.send_message(message.from_user.id, text=success_text)
    await state.clear()


"""
Callback handlers for 'settings' functionality
"""


@router.callback_query(lambda c: c.data == "language")
async def language(call: types.CallbackQuery, user: User):
    if call.data == 'language':
        lang = user.language
        language_text = get_translation(
            lang,
            'language_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=language_text, reply_markup=kb.settings_language)


@router.callback_query(lambda c: c.data in ['set_ru', 'set_en', 'set_pl', 'set_uk'])
async def set_language(call: types.CallbackQuery, session: AsyncSession, user: User):
    if call.data in ['set_ru', 'set_en', 'set_pl', 'set_uk']:
        lang = call.data[-2:]
        print(lang)
        await session.execute(
            update(User)
            .where(User.tg_id == call.from_user.id)
            .values(language=lang)
        )
        await session.commit()
        await send_profile(user)


@router.callback_query(lambda c: c.data == "currency")
async def currency(call: types.CallbackQuery, user: User):
    if call.data == 'currency':
        lang = user.language
        currency_text = get_translation(
            lang,
            'currency_message'
        )
        await call.message.delete()
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=currency_text, reply_markup=kb.settings_currency)


@router.callback_query(lambda c: c.data in ["usd", "eur", "pln", "uah", "rub", "byn"])
async def set_currency(call: types.CallbackQuery, user: User, session: AsyncSession):
    if call.data in ["usd", "eur", "pln", "uah", "rub", "byn"]:
        currency = call.data
        await session.execute(
            update(User)
            .where(User.tg_id == call.from_user.id)
            .values(currency=currency)
        )
        await session.commit()
        await send_profile(user)
