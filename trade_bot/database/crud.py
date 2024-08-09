from typing import List, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Order
from aiogram import Bot
import keyboards as kb


async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalars().first()


async def update_user_profile(session: AsyncSession, tg_id: int, **kwargs):
    await session.execute(
        update(User).where(User.tg_id == tg_id).values(**kwargs)
    )


async def register_referal(session: AsyncSession, referer: User, user: User, bot: Bot):
    (await referer.awaitable_attrs.referals).append(user)
    if referer.is_worker:
        await bot.send_message(
            referer.tg_id,
            f'Ваш реферал {user.tg_id} привязан к вашей учетной записи. ',
            reply_markup=kb.get_worker_user_managment_kb(user.id)
        )


async def get_orders_by_tg_id(session: AsyncSession, tg_id: int) -> Sequence[Order]:
    result = await session.execute(select(Order).where(Order.user_tg_id == tg_id))
    return result.scalars().all()

async def add_order(session: AsyncSession, order: Order, user: User):
    (await user.awaitable_attrs.orders).append(order)
    await session.execute(update(User).where(User.tg_id == user.tg_id)
                          .values(balance=User.balance+order.profit))
    session.add_all([order, user])