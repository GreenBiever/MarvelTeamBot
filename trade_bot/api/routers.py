from typing import List
import asyncio
import config
from aiogram import Bot
from database.models import User, Order
from datetime import datetime, time, timedelta
from fastapi import APIRouter, Query, Request, Path, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.schemas import UserProfile, OrderView
from database.crud import get_user_by_tg_id, update_user_profile, add_order
from database.connect import get_session
from sqlalchemy.ext.asyncio import AsyncSession
import datetime as dt
from utils.get_exchange_rate import currency_exchange

from utils.get_exchange_rate import currency_exchange
from database.enums import CurrencyEnum

router = APIRouter()
templates = Jinja2Templates(directory="okx")


async def send_order_notification(user: User, order: Order, session: AsyncSession):
    order_time = timedelta(seconds=order.time)  # order.time должен быть в секундах или приведен к ним
    order_created = order.created_at
    await asyncio.sleep(order.time)
    order_close_time = order_created + order_time
    formatted_time = order_close_time.strftime("%H:%M:%S")

    profit = order.profit
    if profit > 0:
        message = (
            f"✅ Ваша сделка была успешной:\n"
            f"Сумма: {order.amount} {user.currency.value.upper()}\n"
            f"Выигрыш: +{profit} {user.currency.value.upper()}\n"
            f"Валюта: {order.cryptocurrency}\n"
            f"Время закрытия сделки: {formatted_time}"
        )
    else:
        message = (
            f"❌ К сожалению, сделка была проигрышной:\n"
            f"Сумма: {order.amount} {user.currency.value.upper()}\n"
            f"Проигрыш: {profit} {user.currency.value.upper()}\n"
            f"Валюта: {order.cryptocurrency}\n"
            f"Время закрытия сделки: {formatted_time}"
        )

    await bot.send_message(user.tg_id, message)

from main import bot

@router.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request, trade: str = Query(), id: str = Query()):
    return templates.TemplateResponse(
        request=request, name="/ru/index.html", context={"id": id}
    )


@router.post("/user/{user_tg_id}/orders/")
async def add_user_orders(order: OrderView, user_tg_id: int = Path(),
                          session: AsyncSession = Depends(get_session)):
    user = await get_user_by_tg_id(session, user_tg_id)
    order_model = Order(**order.model_dump())
    await currency_exchange.async_init()
    order_model.profit_usd = int(await currency_exchange.convert_to_usd(user.currency, order_model.profit))
    order_model.amount_usd = int(await currency_exchange.convert_to_usd(user.currency, order_model.amount))
    await add_order(session, user=user, order=order_model)
    await session.commit()
    time_str = dt.datetime.now().strftime('%H:%M:%S')
    user_currencty_title = user.currency.value.upper()
    params = (await currency_exchange.get_exchange_rate(user.currency, order.amount),
     user_currencty_title,
      await currency_exchange.get_exchange_rate(user.currency, abs(order.profit)),
       user_currencty_title, order.cryptocurrency, time_str)
    if order.bets_result_win == True:
        text = user.lang_data['text']['order_success']
    else:
        text = user.lang_data['text']['order_fail']
    await bot.send_message(user.tg_id, text.format(*params))
    states = {None: 'Рандом', False: 'Проигрыш', True: 'Выигрыш'}
    await user.send_log(bot, f'''Сделал ставку:\n
ID: <code>{user.tg_id}</code>
Имя: {user.fname or user.lname or '-'}
Ставка: <b>{order.amount} USD</b>
Баланс: <b>{user.balance} USD</b>
Крипта: <code>{order.cryptocurrency}</code>
Время: <code>{order.time.seconds}</code> секунд
Статус: <b>{states[user.bets_result_win]}</b>''')
    await user.send_log(bot, f'''Получен результат ставки\n
ID: <code>{user.tg_id}</code>
Ставка: <b>{order.amount} USD</b>
Текущий Баланс: <b>{round(user.balance, 2)} USD</b>
Профит: <b>{'-' if order.bets_result_win == False else '+'}{order.profit} USD</b>
Время: <code>{time_str}</code>
Крипта: <code>{order.cryptocurrency}</code>''')

@router.get("/user/{user_tg_id}/", response_model=UserProfile)
async def get_user_profile(user_tg_id: int = Path(), session: AsyncSession = Depends(get_session)):
    user = await get_user_by_tg_id(session, user_tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновляем значение balance в объекте user
    user.balance = int(await user.get_balance())

    # Обновляем объект user и возвращаем его
    await session.refresh(user, ['orders'])
    return user


@router.post("/user/profiles/", status_code=204)  # Deprecated
async def set_user_profile(profile: UserProfile,
                           session: AsyncSession = Depends(get_session)):
    await update_user_profile(session, profile.user_tg_id, profile.model_dump())
