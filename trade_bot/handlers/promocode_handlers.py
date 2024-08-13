from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Cancel, Start, Checkbox
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const, Multi
from database.crud import get_promocode_by_code
from database.models import Promocode, UserPromocodeAssotiation


router = Router()

class PromocodeMenu(StatesGroup):
    wait = State()

class CreatePromocode(StatesGroup):
    wait_code = State()
    wait_amount = State()
    wait_type = State() # одноразовый или многоразовый
    delete_menu = State()

class ManagePromocode(StatesGroup):
    select_promocode = State()
    manage_promocode = State()
    delete_promocode = State()


main_dialog = Dialog(
    Window(
        Const("Выберите действие с промокодами:"),
        Start(Const("Создать промокод"), id="create_promocode", state=CreatePromocode.wait_code),
        Start(Const('Список промокодов'), id="get_promocode_list", state=ManagePromocode.select_promocode),
        state=PromocodeMenu.wait,
    )
)

CANCEL_CREATION = Cancel("Отмена создания промокода")
ALLOWED_CHARS = ''

async def on_error_promocode(event, widget, dialog_manager: DialogManager, *_):
    await event.message.answer('Используйте только большие англ. буквы и цифры, длина промокода больше 4 символов:')

async def on_success_promocode(event, widget: TextInput, dialog_manager: DialogManager, **data):
    session = data['session']
    code = widget.get_value()
    if get_promocode_by_code(session, code) is not None:
        data['code_already_exsist'] = True
    else:
        await dialog_manager.next()

async def create_promocode(event, widget, dialog_manager: DialogManager, **data):
    await dialog_manager.done()
    promocode = Promocode(code=dialog_manager.find('promocode_code').get_value(),
                          amount=dialog_manager.find('promocode_amount').get_value(),
                          reusable=dialog_manager.find('promocode_type').is_checked())
    (await promocode.awaitable_attrs.users).append(
        UserPromocodeAssotiation(user=data['user'], is_creator=True))  
    data['session'].add(promocode)

def validate_promocode(code: str):
    text = str(code)
    if len(text) > 4 or not all(t in ALLOWED_CHARS for t in text):
        raise ValueError
    return text

create_promocode_dialog = Dialog(
    Window(
        Multi(Const("Такой промокод уже существует.", when=F.get('code_already_exsist')),
                    Const("Укажите новый промокод:")),
        TextInput(
            id='promocode_code', type_factory=validate_promocode,
            on_success=on_success_promocode, on_error=on_error_promocode
        ),
        CANCEL_CREATION,
        state=CreatePromocode.wait_code
    ),
    Window(
        Const("Введите сумму, которая будет получена при активации промокода(в USD):"),
        TextInput(id='promocode_amount', type_factory=float),
        CANCEL_CREATION,
        state=CreatePromocode.wait_amount
    ),
    Window(
        Const("Выберите тип промокода"),
        Checkbox(Const("Одноразовый"), Const("Многоразовый"), id='promocode_type'),
        Button("Создать промокод", id="create_promocode", ),
        CANCEL_CREATION,
        state=CreatePromocode.wait_type
    ),



)

@router.message(F.text == '1010')
async def cmd_activate_user_promocode_dialog(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(PromocodeMenu.wait)