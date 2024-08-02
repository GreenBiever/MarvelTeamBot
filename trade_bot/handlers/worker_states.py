from aiogram.fsm.state import StatesGroup, State


class SendMailing(StatesGroup):
    waiting = State()

class CreatePromocode(StatesGroup):
    wait_code = State()
    wait_amount = State()
    wait_type = State() # одноразовый или многоразовый

class SetAmount(StatesGroup):
    wait_amount = State()

class TopUpBalance(StatesGroup):
    wait_amount = State()

class SetWithdraw(StatesGroup):
    wait_amount = State()

class SetMinDeposit(StatesGroup):
    wait_amount = State()
    