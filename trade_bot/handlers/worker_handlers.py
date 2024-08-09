from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
import keyboards as kb
from middlewares import AuthorizeMiddleware, WorkerInjectTargetUserMiddleware
from database.models import User, Order
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink
import random
from database.enums import LangEnum, CurrencyEnum
from sqlalchemy.ext.asyncio import AsyncSession
from functools import wraps


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())

def get_order_string_representation(order: Order):
    return f'''🗓 Дата и время: {order.created_at}
📍 Ставка: {order.amount} USD
💰 Профит:  {order.profit} USD
🖇 Предмет: {order.cryptocurrency}
🕔 Время: {order.time.seconds} сек.'''

async def get_string_user_representation(user: User, worker: User):
    states = {None: 'Рандом', False: 'Проигрыш', True: 'Выигрыш'}
    return f'''🆔 Id: {user.tg_id} {f'\n👦 Username: @{user.username}'
                                     if user.username else ''}
👨‍💻 Воркер: {worker.tg_id}
💰 Баланс: {user.balance} USD
 ∟Мин. вывод: {user.min_withdraw} USD
🔝 Максимальный баланс: {user.max_balance} USD
💸 Минимальная сумма пополнения: {user.min_deposit} USD
📑 Верификация: {'✅' if user.is_verified else '❌'}
📊 Статус торгов: {'✅' if not user.bidding_blocked else '❌'}
💰 Статус вывода: {'✅' if not user.withdraw_blocked else '❌'}
🎰 Статус: {states[user.bets_result_win]}

📊 Последняя ставка:
{get_order_string_representation((await user.awaitable_attrs.orders)[-1])}
'''


@router.message(F.text == 'Воркер')
async def cmd_worker(message: Message, user: User, session: AsyncSession):
    await message.answer('Привет, воркер!',
                          reply_markup=kb.get_main_worker_kb())
    user.is_worker = True
    session.add(user)


@router.callback_query(F.data == 'worker_back')
async def cmd_worker_back(callback: CallbackQuery, user: User, session: AsyncSession):
    await callback.message.edit_reply_markup(reply_markup=kb.get_main_worker_kb())

@router.callback_query(F.data == 'worker_list')
async def cmd_worker_list(callback: CallbackQuery, user: User, session: AsyncSession):
    await callback.message.edit_reply_markup(
        reply_markup=kb.get_worker_select_user_kb(await user.awaitable_attrs.referals)
    )


@router.callback_query(F.data.startswith('worker_user_'))
async def select_target_user(callback: CallbackQuery, user: User, session: AsyncSession):
    target_uid = int(callback.data.split('_')[-1])
    target = await session.get(User, target_uid)
    await callback.message.edit_reply_markup(
        reply_markup=kb.get_worker_user_managment_kb(target)
    )

@router.callback_query(F.data.startswith("worker_unbind_"))
async def unbind_user(callback: CallbackQuery, user: User, session: AsyncSession):
    target = await session.get(User, int(callback.data.split('_')[-1]))
    target.referer = None
    session.add_all([target, user])
    await callback.message.edit_message("Реферал удален", 
        reply_markup=kb.get_worker_menu_back_kb())