import asyncio
import random
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile, CallbackQuery

from nft_bot.databases.crud import get_promocode, activate_promocode
from nft_bot.keyboards import kb
from nft_bot.main import translations, get_translation, send_profile
from nft_bot.databases import requests
from nft_bot.states import deposit_state, withdraw_state
from nft_bot import config
from databases.models import User, Promocode, Purchased
from nft_bot.middlewares import AuthorizeMiddleware
from nft_bot.utils.main_bot_api_client import main_bot_api_client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from nft_bot.databases.enums import CurrencyEnum

bot: Bot = Bot(config.TOKEN)
router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())


class EnterPromocode(StatesGroup):
    wait_promocode = State()


"""
Callback handlers for 'PROFILE' button
"""


@router.message(F.text.in_({"💼 Личный кабинет", "💼 Profile", "💼 Profil", "💼 Профіль"}))
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
async def favourites(call: types.CallbackQuery, user: User, session: AsyncSession):
    try:
        await call.message.delete()
        lang = user.language
        keyboard = await kb.create_favourites_kb(session, user.id)
        favourites_text = get_translation(lang, 'favourites_message')
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, photo=photo, caption=favourites_text, reply_markup=keyboard)
    except Exception as e:
        # Log or handle the error as needed
        print(f"Error handling favourites: {e}")



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
async def my_nft(call: types.CallbackQuery, user: User, session: AsyncSession):
    if call.data == 'my_nft':
        lang = user.language
        # Check if there are any purchased NFTs for the user
        result = await session.execute(
            select(Purchased).where(Purchased.user_id == user.id)
        )
        purchased_items = result.scalars().all()

        if not purchased_items:
            # No purchased items found, send the alert message
            my_nft_text = get_translation(
                lang,
                'my_nft_message'
            )
            await call.answer(my_nft_text, show_alert=False)
        else:
            # Purchased items found, create and send the NFT keyboard
            keyboard = await kb.create_my_nft_kb(session, user.id)
            photo = FSInputFile(config.PHOTO_PATH)
            my_nft_text = get_translation(
                lang,
                'my_nft_message2'
            )
            await bot.send_photo(call.from_user.id, photo=photo, caption=my_nft_text, reply_markup=keyboard)


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
        if user.referer_id is not None:
            await bot.send_message(user.referer.tg_id, text=f'Пользователь {user.tg_id} нажал на пополнение баланса!')
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
        payment_props = await main_bot_api_client.get_payment_props()

        success_text = get_translation(lang,
                                       'card_deposit_message',
                                       card_number=payment_props.card if payment_props else '❌',
                                       comment='test_comment')  # предполагаем, что есть перевод для этого сообщения
        photo = FSInputFile(config.PHOTO_PATH)
        keyboard = kb.create_card_crypto_kb(lang)
        await bot.send_photo(message.from_user.id, caption=success_text, photo=photo, reply_markup=keyboard)
        await state.update_data(amount=message.text)
        await state.clear()


@router.callback_query(lambda c: c.data in ['usdt', 'btc', 'eth'])
async def choose_crypto(call: types.CallbackQuery, user: User):
    if call.data in ['usdt', 'btc', 'eth']:
        crypto_min_prices = {
            'btc': 0.001,
            'eth': 0.015,
            'usdt': 20,
        }
        lang = user.language
        payment_props = await main_bot_api_client.get_payment_props()
        if not payment_props:
            crypto_props = {}
        else:
            crypto_props = {
                'btc': payment_props.btc_wallet,
                'eth': payment_props.eth_wallet,
                'usdt': payment_props.usdt_trc20_wallet
            }
        currency = call.data.split('_')[-1]
        currency_title = currency.upper()
        crypto_text = get_translation(
            lang,
            'crypto_deposit_message',
            currency_title=currency_title,
            crypto_min_price=crypto_min_prices[currency],
            crypto_address=crypto_props.get(currency, '❌')
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
    if user.referer_id is not None:
        await bot.send_message(user.referer.tg_id,
                               text=f'Пользователь {user.tg_id} хочет вывести эту сумму: {amount}!')
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


@router.callback_query(F.data == 'promocode')
async def cmd_promocode(cb: CallbackQuery, state: FSMContext, user: User):
    text = get_translation(user.language, 'promocode_message')
    await cb.message.delete()
    await bot.send_message(cb.from_user.id, text, reply_markup=kb.profile_back)
    await state.set_state(EnterPromocode.wait_promocode)


@router.message(F.text, EnterPromocode.wait_promocode)
async def set_promocode(message: Message, state: FSMContext, user: User,
                        session: AsyncSession, bot: Bot):
    await state.clear()
    promocode = await get_promocode(session, user, message.text)
    if not promocode:
        await message.answer(get_translation(user.language, 'promocode_error_message'),
                             reply_markup=kb.profile_back)
    else:
        await activate_promocode(session, user, promocode)
        await message.answer(get_translation(user.language, 'promocode_success_message'),
                             reply_markup=kb.profile_back)
        if user.referer_id is not None:
            await bot.send_message(user.referer.tg_id,
                                f"Успешная активация промокода <code>{promocode.code}</code>"
                                f" на сумму <b>{promocode.amount} $</b>")


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
        user.language = lang
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
        user.currency = currency
        await send_profile(user)

