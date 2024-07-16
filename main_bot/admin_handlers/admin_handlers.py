from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile,  CallbackQuery
from main_bot.middlewares import IsVerifiedMiddleware, AuthorizeMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from main_bot.services.images import image_generator
from main_bot.database.models import User, PaymentDetails
from main_bot import config
from main_bot.keyboards import kb
from sqlalchemy import select

router = Router()
router.message.middleware(AuthorizeMiddleware())
router.message.middleware(IsVerifiedMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())
router.callback_query.middleware(IsVerifiedMiddleware())


@router.message(F.text == '🧐 Админ панель')
async def admin_panel(message: Message, user: User):
    if user.tg_id in config.ADMIN_IDS:
        await message.answer('Открыта админ-панель!', reply_markup=kb.admin_panel)


@router.message(F.text == 'Пользователи')
async def users(message: Message, user: User, bot: Bot, session: AsyncSession):
    if user.tg_id in config.ADMIN_IDS:
        # Получаем список всех пользователей
        result = await session.execute(select(User))
        users = result.scalars().all()

        # Форматируем данные в удобный табличный вид
        if users:
            text = "Список пользователей:\n\n"
            for user in users:
                text += f'ID: {user.id}\nTG ID: {user.tg_id}\nИмя: {user.fname or ""}\nФамилия: {user.lname or ""}\nUsername: {user.username or ""}\nБаланс: {user.balance}\nПроверен: {"Да" if user.is_verified else "Нет"}\nЗаблокирован: {"Да" if user.is_blocked else "Нет"}\n\n'
        else:
            text = "Пользователей не найдено."

        # Отправляем сообщение с пользователями
        await message.answer(text=text)


@router.message(F.text == 'Реквизиты')
async def details(message: Message, user: User):
    if user.tg_id in config.ADMIN_IDS:
        await message.answer('Выберите сервис для добавления реквизитов: ', reply_markup=kb.services_details)


@router.callback_query(F.data.startswith('details_service|'))
async def choose_service(call: CallbackQuery, user: User, session: AsyncSession):
    global service_name
    service_id = call.data.split('|')[1]
    if service_id == '1':
        service_name = '💼 Трейд бот'
    elif service_id == '2':
        service_name = '🎆 NFT бот'

    # Получение деталей оплаты для выбранной услуги
    result = await session.execute(select(PaymentDetails).where(PaymentDetails.service_id == int(service_id)))
    payment_details = result.scalars().all()

    # Форматирование данных в текст
    if payment_details:
        text = f"Детали оплаты для {service_name}:\n\n"
        for detail in payment_details:
            text += f"Тип: {detail.type}\nНомер счета: {detail.account_number}\n\n"
    else:
        text = f"Детали оплаты для {service_name} не найдены."

    # Отправка сообщения пользователю
    await call.message.answer(text=text)

