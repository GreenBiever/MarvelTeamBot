from main_bot.api.schemas import ReferalModel
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from main_bot.database.models import User, OrdinaryUser
from datetime import datetime


async def get_user_by_tg_id(session: AsyncSession, tg_id: int):
    return await session.scalar(select(User).where(User.tg_id == tg_id))


async def add_referal(session: AsyncSession, referal: ReferalModel):
    new_referal = OrdinaryUser(tg_id = referal.referal_tg_id,
                               fname = referal.fname, lname = referal.lname,
                               username = referal.username)
    referer = await get_user_by_tg_id(session, referal.referal_link_id)
    (await referer.awaitable_attrs.ordinary_users).append(new_referal)
    session.add_all([new_referal, referer])
    await session.commit()

async def get_user_by_their_referal(session: AsyncSession, referal_tg_id: int) -> User | None:
    ordinary_user = await session.scalar(select(OrdinaryUser)
                             .where(OrdinaryUser.tg_id == referal_tg_id)
                             .options(selectinload(OrdinaryUser.regulatory_user)))
    return ordinary_user.regulatory_user