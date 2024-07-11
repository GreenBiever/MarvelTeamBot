from nft_bot.config import SQLALCHEMY_URL
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from nft_bot.utils.get_exchange_rate import currency_exchange
from .enums import CurrencyEnum

engine = create_async_engine(SQLALCHEMY_URL, echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str] = mapped_column()
    language: Mapped[str] = mapped_column()
    balance: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[CurrencyEnum] = mapped_column(default=CurrencyEnum.usd)
    message_id: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()
    verification: Mapped[str] = mapped_column()

    async def get_balance(self) -> float:
        '''retun user balance converted to user currency'''
        return await currency_exchange.get_exchange_rate(self.currency, self.balance)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    products = relationship('Product', back_populates='category')


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    price: Mapped[str] = mapped_column()
    author: Mapped[str] = mapped_column()
    photo: Mapped[str] = mapped_column()
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category = relationship('Category', back_populates='products')

    async def get_product_price(self) -> float:
        '''retun user balance converted to user currency'''
        return await currency_exchange.get_exchange_rate(User.currency, self.price)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
