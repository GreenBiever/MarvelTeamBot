from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
import keyboards as kb
from middlewares import AuthorizeMiddleware
from database.models import User
from .states import TopUpBalanceWithCard, WithdrawBalance, EnterPromocode
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from utils.main_bot_api_client import main_bot_api_client


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())


@router.callback_query(F.data == 'wallet')
async def cmd_open_wallet(cb: CallbackQuery, user: User):
    text = user.lang_data['text']['wallet'].format(user.tg_id,
                                                   await user.get_balance(),
                                                   user.currency.value.upper())
    await cb.message.edit_text(text, reply_markup=kb.get_wallet_kb(user.lang_data))

@router.callback_query(F.data == 'top_up')
async def cmd_top_up(cb: CallbackQuery, user: User):
    text = user.lang_data['text']['select_payment']
    await cb.message.edit_text(text, reply_markup=kb.get_top_up_kb(user.lang_data))

@router.callback_query(F.data == 'card')
async def top_up_with_card(cb: CallbackQuery, state: FSMContext, user: User):
    await state.set_state(TopUpBalanceWithCard.wait_amount)
    await cb.message.edit_text(user.lang_data['text']['enter_amount'])

@router.message(F.text, TopUpBalanceWithCard.wait_amount)
async def set_amount(message: Message, state: FSMContext, user: User):
    await state.clear()
    payment_props = await main_bot_api_client.get_payment_props()
    await message.answer(
        user.lang_data['text']['card_deposit_info'].format(
              payment_props.card if payment_props else '❌', user.tg_id),
              reply_markup=kb.get_support_kb(user.lang_data)
              )
    
@router.callback_query(F.data == 'crypto')
async def top_up_with_crypto(cb: CallbackQuery, user: User):
    await cb.message.edit_text(user.lang_data['text']['select_crypto_currency'], 
                               reply_markup=kb.get_select_crypto_currency_kb(user.lang_data))
    
@router.callback_query(F.data.startswith('crypto_currency_'))
async def pay_with_crypto(cb: CallbackQuery, user: User):
    crypto_min_prices = {
        'btc': 0.001,
        'eth': 0.015,
        'usdt': 20,
    }
    payment_props = await main_bot_api_client.get_payment_props()
    if not payment_props: crypto_props = {}
    else:
        crypto_props = {
            'btc': payment_props.btc_wallet,
            'eth': payment_props.eth_wallet,
            'usdt': payment_props.usdt_trc20_wallet
        }
    currency = cb.data.split('_')[-1]
    currency_title = currency.upper()
    
    text = user.lang_data['text']['crypto_deposit_details'].format(
        currency_title, crypto_min_prices[currency], currency_title,
        crypto_props.get(currency, '❌'), currency_title
    )
    await cb.message.edit_text(text, reply_markup=kb.get_support_kb(user.lang_data))

@router.callback_query(F.data == 'withdraw')
async def cmd_withdraw(cb: CallbackQuery, state: FSMContext, user: User):
    await cb.message.edit_text(user.lang_data['text']['enter_withdraw_amount'],
                                reply_markup=kb.get_back_kb(user.lang_data))
    await state.set_state(WithdrawBalance.wait_amount)

@router.message(F.text, WithdrawBalance.wait_amount)
async def set_amount_of_withdraw(message: Message, state: FSMContext, user: User):
    #await state.clear()
    await message.answer(user.lang_data['text']['withdraw_error'])
    

@router.callback_query(F.data == 'promocode')
async def cmd_promocode(cb: CallbackQuery, state: FSMContext, user: User):
    text = user.lang_data['text']['enter_promocode']
    await cb.message.edit_text(text, reply_markup=kb.get_back_kb(user.lang_data))
    await state.set_state(EnterPromocode.wait_promocode)

@router.message(F.text, EnterPromocode.wait_promocode)
async def set_promocode(message: Message, state: FSMContext, user: User,
                        session: AsyncSession):
    await state.clear()
    promocode_response = await main_bot_api_client.activate_promocode(
        code=message.text, tg_id=user.tg_id
    )

    if not promocode_response.available:
        await message.answer(user.lang_data['text']['promocode_error'],
                             reply_markup=kb.get_back_kb(user.lang_data))
    else:
        promocode = promocode_response.promocode
        await user.top_up_balance(session, promocode.amount)
        await message.answer(
            user.lang_data['text']['promocode_success'].format(promocode.amount),
            reply_markup=kb.get_back_kb(user.lang_data)
        )


@router.callback_query(F.data == 'check_payment')
async def cmd_check_payment(cb: CallbackQuery, user: User):
    await cb.message.edit_text(
        user.lang_data['text']['check_payment'],
        reply_markup=kb.get_back_kb(user.lang_data))