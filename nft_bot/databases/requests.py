from nft_bot.databases.models import User, Product, Category, async_session, Favourites
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
from .enums import CurrencyEnum


async def get_user_id(session: AsyncSession, user: User, user_id: int):
    result = await session.execute(select(user).where(user.user_id == user_id))
    return result


async def add_user(session: AsyncSession, user: User, user_id: int, user_name: str, language: str):
    await session.execute(
        insert(user).values(user_id=user_id, user_name=user_name, language=language, balance=0,
                            message_id=0, status='new',
                            verification=0))
    await session.commit()


async def get_user_language(session: AsyncSession, user: User, user_id: int):
    result = await session.execute(select(user.language).where(user.user_id == user_id))
    return result.scalars().first()


async def get_user_info(session: AsyncSession, user: User, user_id: int):
    result = await session.execute(select(user).where(user.user_id == user_id))
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


async def get_user_currency(session: AsyncSession, user: User, user_id: int):
    result = await session.execute(select(user.currency).where(user.user_id == user_id))
    return result.scalars().first()


async def get_user_status(session: AsyncSession, user: User, user_id: int):
    result = await session.execute(select(user.status).where(user.user_id == user_id))
    return result.scalars().first()


async def update_user_language(session: AsyncSession, user: User, user_id: int, language: str):
    stmt = (
        update(user).
        where(user.user_id == user_id).
        values(language=language)
    )
    await session.execute(stmt)
    await session.commit()


async def update_user_currency(session: AsyncSession, user: User, user_id: int, currency: str):
    stmt = (
        update(user).
        where(user.user_id == user_id).
        values(currency=currency)
    )
    await session.execute(stmt)
    await session.commit()


async def add_category(session: AsyncSession, category: Category, category_name: str):
    await session.execute(
        insert(category).values(name=category_name))
    await session.commit()


async def add_item(session: AsyncSession, product: Product, item_name: str, description: str, price: float, author: str,
                   photo: str, category_id: int):
    await session.execute(
        insert(product).values(name=item_name, description=description, price=price, author=author, photo=photo,
                               category_id=category_id))
    await session.commit()


async def get_categories(session: AsyncSession, category: Category):
    result = await session.execute(select(category))
    print(result.scalars().all)
    return result.scalars().all()


async def delete_category(session: AsyncSession, category: Category, category_id: int):
    stmt = (
        delete(category).
        where(category.id == category_id)
    )
    await session.execute(stmt)
    await session.commit()


async def get_items(session: AsyncSession, product: Product):
    result = await session.execute(select(product))
    return result.scalars().all()


async def delete_item(session: AsyncSession, product: Product, item_id: int):
    stmt = (
        delete(product).
        where(product.id == item_id)
    )
    await session.execute(stmt)
    await session.commit()


async def get_category_count(session: AsyncSession, category: Category):
    result = await session.execute(select(func.count(category.id)))
    count = result.scalar()
    return count


async def get_categories_with_item_count(session: AsyncSession, category: Category, product: Product):
    result = await session.execute(
        select(category.id, category.name, func.count(product.id).label('item_count'))
        .join(product, category.id == product.category_id, isouter=True)  # Left join with Product table
        .group_by(category.id)
    )
    categories_with_count = result.all()
    return categories_with_count


async def get_categories_with_item_count_by_id(session: AsyncSession, category: Category, product: Product,
                                               category_id: int):
    result = await session.execute(
        select(category.id, category.name, func.count(product.id).label('item_count')).where(category.id == category_id)
        .join(product, category.id == product.category_id, isouter=True)  # Left join with Product table
        .group_by(category.id)
    )
    categories_with_count = result.all()
    return categories_with_count


async def get_items_by_category_id(session: AsyncSession, product: Product, category_id: int):
    result = await session.execute(select(product).where(product.category_id == category_id))
    items = result.scalars().all()
    return items


async def get_item_info(session: AsyncSession, product: Product, category: Category, item_id: int):
    result = await session.execute(
        select(product.id, product.name, product.description, product.price, product.author, product.photo,
               category.name.label('category_name'))
        .join(category, product.category_id == category.id)
        .where(product.id == item_id)
    )
    product_info = result.one_or_none()
    return product_info


async def add_to_favourites(session: AsyncSession, favourites: Favourites, user_id: int, item_id: int):
    await session.execute(
        insert(favourites).values(user_id=user_id, item_id=item_id))
    await session.commit()


async def register_referal(session: AsyncSession, referer: User, user: User):
    (await referer.awaitable_attrs.referals).append(user)
