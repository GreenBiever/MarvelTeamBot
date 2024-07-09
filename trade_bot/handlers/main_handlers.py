from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import keyboards as kb
from middlewares import AuthorizeMiddleware
from database.models import User
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())

async def get_greeting(message: Message, user: User, edited_message: Message = None):
    text = f'''
📂 Портфель:

💵 Баланс: {user.balance} UAH # TODO
🗣 Имя: {user.fname}

📝Верификация: {"❌" if not user.is_verified else "Да"}

🍀 Рефералов: 0 # TODO
🟢 Активных сделок на площадке: 1014 # TODO

{hlink('Реферальная ссылка', f'https://t.me/Okx_Company_bot?start={user.tg_id}')}
'''
    if not edited_message:
        await message.answer(text, reply_markup=kb.get_main_kb(), parse_mode='HTML')
    else:
        await edited_message.edit_text(text, reply_markup=kb.get_main_kb(),
                                        parse_mode='HTML')

@router.message(Command('start'))
async def cmd_start(message: Message, user: User):
    await get_greeting(message, user)

@router.callback_query(F.data == 'back')
async def cmd_back(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    await get_greeting(cb.message, user, cb.message)

