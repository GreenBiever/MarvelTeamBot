from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import keyboards as kb
from middlewares import AuthorizeMiddleware
from database.models import User
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink
import random
from database.enums import LangEnum, CurrencyEnum
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())


@router.message(F.text == 'Воркер')
async def cmd_worker(message: Message, user: User):
    await message.answer('Привет, воркер!',
                          reply_markup=kb.get_worker_main_kb())