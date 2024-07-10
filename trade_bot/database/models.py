from sqlalchemy.orm import Mapped, mapped_column
from .connect import Base
from datetime import datetime
from .enums import LangEnum, CurrencyEnum
from utils import currency_exchange
from locales import data as lang_data


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str]
    fname: Mapped[str]
    lname: Mapped[str]
    username: Mapped[str]
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

    async def get_balance(self) -> float:
        '''retun user balance converted to user currency'''
        return await currency_exchange.get_exchange_rate(self.currency, self.balance)


    @property
    def lang_data(self) -> dict:
        return lang_data[self.language]