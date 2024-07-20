from aiogram.fsm.state import StatesGroup, State


class ControlUsers(StatesGroup):
    user_id = State()
    write_message = State()


class AddPaymentDetails(StatesGroup):
    service = State()
    type = State()
    details = State()


class DeletePayment(StatesGroup):
    id = State()


class Mailing(StatesGroup):
    text = State()