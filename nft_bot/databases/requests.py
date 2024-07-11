from nft_bot.databases.models import User, Product, Category, async_session
from sqlalchemy import select, insert, update, delete, func
from .enums import CurrencyEnum


async def get_user_id(user_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        return result


async def add_user(user_id, user_name, language):
    async with async_session() as session:
        await session.execute(
            insert(User).values(user_id=user_id, user_name=user_name, language=language, balance=0,
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


async def get_user_currency(user_id):
    async with async_session() as session:
        result = await session.execute(select(User.currency).where(User.user_id == user_id))
        return result.scalars().first()


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
            insert(Product).values(name=item_name, description=description, price=price, author=author, photo=photo,
                                   category_id=category_id, ))
        await session.commit()


async def get_categories():
    async with async_session() as session:
        result = await session.execute(select(Category))
        print(result.scalars().all)
        return result.scalars().all()


async def delete_category(category_id):
    async with async_session() as session:
        stmt = (
            delete(Category).
            where(Category.id == category_id)
        )
        await session.execute(stmt)
        await session.commit()


async def get_items():
    async with async_session() as session:
        result = await session.execute(select(Product))
        return result.scalars().all()


async def delete_item(item_id):
    async with async_session() as session:
        stmt = (
            delete(Product).
            where(Product.id == item_id)
        )
        await session.execute(stmt)
        await session.commit()


async def get_category_count():
    async with async_session() as session:
        result = await session.execute(select(func.count(Category.id)))
        count = result.scalar()
        return count


async def get_categories_with_item_count():
    async with async_session() as session:
        result = await session.execute(
            select(Category.id, Category.name, func.count(Product.id).label('item_count'))
            .join(Product, Category.id == Product.category_id, isouter=True)  # Left join with Product table
            .group_by(Category.id)
        )
        categories_with_count = result.all()
        return categories_with_count


async def get_categories_with_item_count_by_id(category_id):
    async with async_session() as session:
        result = await session.execute(
            select(Category.id, Category.name, func.count(Product.id).label('item_count')).where(Category.id == category_id)
            .join(Product, Category.id == Product.category_id, isouter=True)  # Left join with Product table
            .group_by(Category.id)
        )
        categories_with_count = result.all()
        return categories_with_count


async def get_items_by_category_id(category_id):
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.category_id == category_id))
        items = result.scalars().all()
        return items


async def get_item_info(item_id):
    async with async_session() as session:
        result = await session.execute(
            select(Product.id, Product.name, Product.description, Product.price, Product.author, Product.photo, Category.name.label('category_name'))
            .join(Category, Product.category_id == Category.id)
            .where(Product.id == item_id)
        )
        product_info = result.one_or_none()
        return product_info

