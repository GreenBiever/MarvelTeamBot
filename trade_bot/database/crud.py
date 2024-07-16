from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User


async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalars().first()


async def update_user_profile(session: AsyncSession, tg_id: int, **kwargs):
    await session.execute(
        update(User).where(User.tg_id == tg_id).values(**kwargs)
    )


async def register_referal(session: AsyncSession, referer: User, user: User):
    (await referer.awaitable_attrs.referals).append(user)
