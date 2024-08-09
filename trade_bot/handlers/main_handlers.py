from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import keyboards as kb
from middlewares import AuthorizeMiddleware
from database.models import User
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink
import random
from database.enums import LangEnum, CurrencyEnum
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())

async def get_greeting(message: Message, user: User, edited_message: Message = None,
                       bot_username: str = 'develop_021_bot'):
    text = user.lang_data['text']['greeting'].format(
        await user.get_balance(), user.currency.value.upper(), user.fname,
        "✅" if user.is_verified else "❌", 0, random.randint(100, 1500),
        hlink('Реферальная ссылка', f'https://t.me/{bot_username}?start={user.tg_id}'))
    if not edited_message:
        await message.answer(text, reply_markup=kb.get_main_kb(user.lang_data),
                              parse_mode='HTML')
    else:
        await edited_message.edit_text(text, reply_markup=kb.get_main_kb(user.lang_data),
                                        parse_mode='HTML')

@router.message(Command('start'))
async def cmd_start(message: Message, user: User):
    await get_greeting(message, user)

@router.callback_query(F.data == 'change_lang')
async def cmd_change_lang(cb: CallbackQuery, user: User):
    await cb.message.edit_text(user.lang_data['text']['change_lang'],
                                reply_markup=kb.get_select_lang_kb(user.lang_data))


@router.callback_query(F.data.startswith('set_lang_'))
async def cmd_set_lang(cb: CallbackQuery, user: User, session: AsyncSession):
    lang = cb.data.split('_')[-1]
    user.language = LangEnum[lang]
    session.add(user)
    await get_greeting(cb.message, user, cb.message)

@router.callback_query(F.data == 'change_currency')
async def cmd_change_currency(cb: CallbackQuery, user: User, session: AsyncSession):
    await cb.message.edit_text(user.lang_data['text']['change_currency'], 
                               reply_markup=kb.get_select_currency_kb(user.lang_data))

@router.callback_query(F.data.startswith('set_currency_'))
async def cmd_set_currency(cb: CallbackQuery, user: User, session: AsyncSession):
    currency = cb.data.split('_')[-1]
    user.currency = CurrencyEnum[currency]
    session.add(user)
    await get_greeting(cb.message, user, cb.message)

@router.callback_query(F.data == 'back')
async def cmd_back(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    await get_greeting(cb.message, user, cb.message)

@router.callback_query(F.data == 'trade')
async def cmd_trade(cb: CallbackQuery, user: User):
    await cb.message.edit_text(user.lang_data['text']['select_crypto_investment'],
                                reply_markup=kb.get_trade_kb(user.lang_data, user.tg_id))
    
@router.callback_query(F.data == 'trade_faq')
async def cmd_trade_faq(cb: CallbackQuery, user: User):
    await cb.message.edit_text(user.lang_data['text']['trade_faq'],
                                reply_markup=kb.get_back_kb(user.lang_data))
    
@router.callback_query(F.data == 'support')
async def cmd_support(cb: CallbackQuery, user: User):
    await cb.message.edit_text(user.lang_data['text']['support'],
                                reply_markup=kb.get_support_page_kb(user.lang_data))