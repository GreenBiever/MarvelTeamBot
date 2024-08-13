from typing import List, Sequence

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from databases.models import User, Promocode, UserPromocodeAssotiation
from nft_bot.databases.enums import CurrencyEnum
from aiogram import Bot
import nft_bot.keyboards as kb


async def get_created_promocodes(session: AsyncSession, user: User):
    return (await session.execute(
        select(Promocode)
        .join(UserPromocodeAssotiation, Promocode.users)
        .where(UserPromocodeAssotiation.user_id == user.id,
               UserPromocodeAssotiation.is_creator == True)
    )).scalars().all()


async def get_promocode(session: AsyncSession, user: User, code: str) -> Promocode | None:
    '''return promocode if it exsist and user not activated it yet'''
    promocode = await session.scalar(
        select(Promocode)
        .where(Promocode.code == code)
        .options(selectinload(Promocode.users))
    )
    if not promocode: return
    assotiation = await session.scalar(
        select(Promocode)
        .join(UserPromocodeAssotiation, Promocode.users)
        .where(Promocode.id == promocode.id,
               UserPromocodeAssotiation.user_id == user.id)
    )
    if assotiation: return  # Yet activated by this user
    return promocode


async def activate_promocode(session: AsyncSession, user: User, promocode: Promocode
                             ) -> None:
    '''Activate promocode'''
    if promocode.reusable:
        promocode.users.append(UserPromocodeAssotiation(user=user))
        session.add(promocode)
    else:
        await session.delete(promocode)
    await user.top_up_balance(session, promocode.amount)
    session.add(user)


async def get_promocode_by_code(session: AsyncSession, code: str) -> Promocode | None:
    return await session.scalar(select(Promocode).where(Promocode.code == code))
