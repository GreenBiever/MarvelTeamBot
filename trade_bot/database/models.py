from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, select, update
from .connect import Base
from datetime import datetime, timedelta
from .enums import LangEnum, CurrencyEnum
from utils import currency_exchange
from locales import data as lang_data
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import config


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(unique=True)
    fname: Mapped[str | None]
    lname: Mapped[str | None]
    username: Mapped[str | None]
    language: Mapped[LangEnum] = mapped_column(default=LangEnum.ru)
    balance: Mapped[int] = mapped_column(default=0)
    currency: Mapped[CurrencyEnum] = mapped_column(default=CurrencyEnum.usd)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    last_login: Mapped[datetime] = mapped_column(default=datetime.now)

    # On web-site
    purchase_enabled: Mapped[bool] = mapped_column(default=True) 
    output_enabled: Mapped[bool] = mapped_column(default=True)
    min_deposit: Mapped[int] = mapped_column(default=100)
    min_withdraw: Mapped[int] = mapped_column(default=100)
    max_balance: Mapped[int] = mapped_column(default=1000000)

    referer_id: Mapped[Optional['User']] = mapped_column(ForeignKey('users.id'))
    referals: Mapped[list['User']] = relationship('User', back_populates='referer')
    referer: Mapped[Optional['User']] = relationship('User', back_populates='referals',
                                                   remote_side=[id])
    
    is_worker: Mapped[bool] = mapped_column(default=False)
    bets_result_win: Mapped[bool | None] = mapped_column(default=None)
    # None - random, False - lose, True - win
    withdraw_blocked: Mapped[bool] = mapped_column(default=False)
    bidding_blocked: Mapped[bool] = mapped_column(default=False)
    orders: Mapped[list['Order']] = relationship('Order', back_populates='user')
    
    async def top_up_balance(self, session: AsyncSession, amount: int):
        """
        Asynchronously tops up the balance of the user by the specified amount.
        """
        await session.execute(
            update(User).where(User.tg_id == self.tg_id)
            .values(balance=User.balance + amount)
        )
        if (referer := await self.awaitable_attrs.referer) is not None:
            await session.execute(
                update(User).where(User.tg_id == referer.tg_id)
                .values(balance=User.balance + amount * config.REFERAL_BONUS_PERCENT)
            )

    async def get_balance(self) -> float:
        '''retun user balance converted to user currency'''
        return await currency_exchange.get_exchange_rate(self.currency, self.balance)


    @property
    def lang_data(self) -> dict:
        return lang_data[self.language]


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    cryptocurrency: Mapped[str | None]
    amount: Mapped[int] = mapped_column(default=0)

    bets_result_win: Mapped[bool]
    # False - lose, True - win

    profit: Mapped[int] # Profit in USD, may be less than 0 if bets_resut_win is False
    time: Mapped[timedelta] = mapped_column(default=timedelta(seconds=15))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Define the relationship to the User model
    user: Mapped[User] = relationship('User', back_populates='orders')
