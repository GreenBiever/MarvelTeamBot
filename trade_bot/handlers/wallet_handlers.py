from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
import keyboards as kb
from middlewares import AuthorizeMiddleware
from database.models import User
from .states import TopUpBalanceWithCard, WithdrawBalance, EnterPromocode
from aiogram.fsm.context import FSMContext


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
    await message.answer(
        user.lang_data['text']['card_deposit_info'].format(
              '5375524800614054', user.tg_id),
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

    currency = cb.data.split('_')[-1]
    currency_title = currency.upper()
    text = user.lang_data['text']['crypto_deposit_details'].format(
        currency_title, crypto_min_prices[currency], currency_title,
        '.123avbsd....', currency_title
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
async def set_promocode(message: Message, state: FSMContext, user: User):
    await state.clear()
    await message.answer(user.lang_data['text']['promocode_error'])


@router.callback_query(F.data == 'check_payment')
async def cmd_check_payment(cb: CallbackQuery, user: User):
    await cb.message.edit_text(
        user.lang_data['text']['check_payment'],
        reply_markup=kb.get_back_kb(user.lang_data))