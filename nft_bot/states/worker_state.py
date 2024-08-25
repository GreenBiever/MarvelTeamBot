from aiogram.fsm.state import StatesGroup, State


class WorkerPanel(StatesGroup):
    mamont_id = State()
    referal_ms_text = State()


class WorkerMamont(StatesGroup):
    mamont_id = State()
    balance_amount = State()
    min_deposit = State()
    min_withdraw = State()
    mamont_message = State()