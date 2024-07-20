from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from .connect import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(unique=True)
    fname: Mapped[str | None]
    lname: Mapped[str | None]
    username: Mapped[str | None]
    last_login: Mapped[datetime] = mapped_column(default=datetime.now)
    balance: Mapped[int] = mapped_column(default=0)
    is_verified: Mapped[bool] = mapped_column(default=False)
    ordinary_users: Mapped[list['OrdinaryUser']] = relationship(
        'OrdinaryUser', back_populates='regulatory_user') # аккаунты обычных пользователей
    # которые может регулировать данный пользователь
    is_blocked: Mapped[bool] = mapped_column(default=False)


class OrdinaryUser(Base):
    '''Класс описывает модель пользователя, который не является админом
    и не является пользователем main бота, но который воспльзовался nft или trade ботом'''
    __tablename__ = "ordinary_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(unique=True)
    fname: Mapped[str | None]
    lname: Mapped[str | None]
    username: Mapped[str | None]
    last_login: Mapped[datetime] = mapped_column(default=datetime.now)
    regulatory_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    regulatory_user: Mapped[User | None] = relationship('User', back_populates='ordinary_users')


class PaymentDetails(Base):
    __tablename__ = "payment_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    service: Mapped[str] = mapped_column()
    type:  Mapped[str] = mapped_column()
    account_number: Mapped[str] = mapped_column()