from nft_bot.databases.models import User, Product, Category, async_session
from sqlalchemy import select, insert, update, delete


async def get_user_id(user_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        return result


async def add_user(user_id, user_name, language):
    async with async_session() as session:
        await session.execute(
            insert(User).values(user_id=user_id, user_name=user_name, language=language, balance=0, currency='UAH',
                                message_id=0, status='new',
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


async def update_user_language(user_id, language):
    async with async_session() as session:
        stmt = (
            update(User).
            where(User.user_id == user_id).
            values(language=language)
        )
        await session.execute(stmt)
        await session.commit()


async def update_user_currency(user_id, currency):
    async with async_session() as session:
        stmt = (
            update(User).
            where(User.user_id == user_id).
            values(currency=currency)
        )
        await session.execute(stmt)
        await session.commit()


async def add_category(category_name):
    async with async_session() as session:
        await session.execute(
            insert(Category).values(name=category_name))
        await session.commit()


async def add_item(item_name, description, price, author, photo, category_id):
    async with async_session() as session:
        await session.execute(
            insert(Product).values(name=item_name, description=description, price=price, author=author, photo=photo, category_id=category_id,))
        await session.commit()


async def get_categories():
    async with async_session() as session:
        result = await session.execute(select(Category))
        print(result.scalars().all)
        return result.scalars().all()