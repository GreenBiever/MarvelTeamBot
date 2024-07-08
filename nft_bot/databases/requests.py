from nft_bot.databases.models import User, Product, Category, async_session
from sqlalchemy import select, insert


async def get_user_id(user_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        return result


async def add_user(user_id, user_name, language):
    async with async_session() as session:
        await session.execute(
            insert(User).values(user_id=user_id, user_name=user_name, language=language, balance=0, currency='UAH', message_id=0, status='new',
                                verification=0))
        await session.commit()


async def get_user_language(user_id):
    async with async_session() as session:
        result = await session.execute(select(User.language).where(User.user_id == user_id))
        return result.scalars().first()


async def get_user_info(user_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user_data = result.scalars().one_or_none()
        if user_data:
            user_id = user_data.user_id
            user_name = user_data.user_name
            balance = user_data.balance
            currency = user_data.currency
            status = user_data.status
            verification = user_data.verification
            return (user_data, user_id, user_name, balance, currency, status, verification)
        else:
            return None




async def get_user_status(user_id):
    async with async_session() as session:
        result = await session.execute(select(User.status).where(User.user_id == user_id))
        return result.scalars().first()
