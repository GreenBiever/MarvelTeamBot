from aiogram.fsm.state import StatesGroup, State


class Deposit(StatesGroup):
    amount = State()
    currency = State



class Promocode(StatesGroup):
    promo = State()