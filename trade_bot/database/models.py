from sqlalchemy.orm import Mapped, mapped_column
from .connect import Base
from datetime import datetime
from .enums import LangEnum, CurrencyEnum


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str]
    fname: Mapped[str]
    lname: Mapped[str]
    username: Mapped[str]
    language: Mapped[LangEnum] = mapped_column(default=LangEnum.ru)
    balance: Mapped[int] = mapped_column(default=0)
    currency: Mapped[CurrencyEnum] = mapped_column(default=CurrencyEnum.uah)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    last_login: Mapped[datetime] = mapped_column(default=datetime.now)