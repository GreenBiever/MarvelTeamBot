from aiogram.fsm.state import StatesGroup, State


class WorkerPanel(StatesGroup):
    mamont_id = State()


class WorkerMamont(StatesGroup):
    mamont_id = State()