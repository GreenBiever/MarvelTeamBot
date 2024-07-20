from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from main_bot import config
from main_bot.database.models import User, PaymentDetails
from main_bot.keyboards import kb
from main_bot.middlewares import IsVerifiedMiddleware, AuthorizeMiddleware
from main_bot.admin_handlers.states import ControlUsers, AddPaymentDetails, DeletePayment, Mailing

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
        await message.answer(text=text, reply_markup=kb.control_users)


@router.callback_query(F.data == 'control_users')
async def control_users(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    await call.message.answer('Введите ID пользователя ниже: ')
    await state.set_state(ControlUsers.user_id)


@router.message(StateFilter(ControlUsers.user_id))
async def get_user(message: Message, session: AsyncSession, state: FSMContext):
    user_id = message.text
    result = await session.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    if user:
        if user.is_blocked:
            button_text = 'Разблокировать'
            callback_data = 'unblock'
        else:
            button_text = 'Заблокировать'
            callback_data = 'block'
        user_action_kb = [
            [InlineKeyboardButton(text=button_text, callback_data=f'user|{callback_data}'),
             InlineKeyboardButton(text='Написать сообщение', callback_data=f'user|writemessage')],
            [InlineKeyboardButton(text='Вернуться', callback_data='user|back')]
        ]
        user_action = InlineKeyboardMarkup(inline_keyboard=user_action_kb)
        await message.answer(text=f"ID: {user.id}\nTG ID: {user.tg_id}\nИмя: {user.fname or ''}\n"
                                  f"Фамилия: {user.lname or ''}\nUsername: {user.username or ''}\n"
                                  f"Баланс: {user.balance}\nПроверен: {'Да' if user.is_verified else 'Нет'}\n"
                                  f"Заблокирован: {'Да' if user.is_blocked else 'Нет'}", reply_markup=user_action)
        await state.update_data(user_id=user_id)
    else:
        await message.answer(text='Пользователь не найден.')
        await state.clear()


@router.callback_query(F.data.startswith('user|'))
async def action_user(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    action = call.data.split('|')[1]
    data = await state.get_data()
    user_id = data['user_id']
    if action == 'block':
        await session.execute(update(User).where(User.id == user_id).values(is_blocked=True))
        await session.commit()
        await call.message.answer(text='Пользователь заблокирован.')
    elif action == 'unblock':
        await session.execute(update(User).where(User.id == user_id).values(is_blocked=False))
        await session.commit()
        await call.message.answer(text='Пользователь разблокирован.')
    elif action == 'writemessage':
        await call.message.answer(text='Введите сообщение ниже:')
        await state.set_state(ControlUsers.write_message)
    elif action == 'back':
        await call.answer('Открыта админ-панель!', reply_markup=kb.admin_panel)
        await state.clear()


@router.message(StateFilter(ControlUsers.write_message))
async def write_message(message: Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    user = await session.execute(select(User).where(User.id == user_id))
    user = user.scalars().first()
    if user:
        await message.bot.send_message(user.tg_id, text=message.text)
        await message.delete()
        await message.delete()
        await message.answer(text='Сообщение отправлено.')

    else:
        await message.answer(text='Пользователь не найден.')


@router.message(F.text == 'Реквизиты')
async def details(message: Message, user: User):
    if user.tg_id in config.ADMIN_IDS:
        await message.answer('Выберите сервис для добавления реквизитов: ', reply_markup=kb.services_details)


@router.callback_query(F.data.startswith('details_service|'))
async def choose_service(call: CallbackQuery, user: User, session: AsyncSession, state: AddPaymentDetails.service):
    await call.message.delete()
    global service_name
    service_id = call.data.split('|')[1]
    if service_id == '1':
        service_name = '💼 Трейд бот'
        service_id = 'trade'
        await state.update_data(service='trade')
    elif service_id == '2':
        service_name = '🎆 NFT бот'
        service_id = 'nft'
        await state.update_data(service='nft')

    # Получение деталей оплаты для выбранной услуги
    result = await session.execute(select(PaymentDetails).where(PaymentDetails.service == service_id))
    payment_details = result.scalars().all()

    # Форматирование данных в текст
    if payment_details:
        text = f"Детали оплаты для {service_name}:\n\n"
        for detail in payment_details:
            text += f"ID: {detail.id} Тип: {detail.type}\nНомер счета: {detail.account_number}\n\n"
    else:
        text = f"Детали оплаты для {service_name} не найдены."

    # Отправка сообщения пользователю
    await call.message.answer(text=text, reply_markup=kb.add_payment_details)


@router.callback_query(F.data == 'add_payment_details')
async def add_payment_details(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer('Выберите метод оплаты для пополнения: ', reply_markup=kb.add_payment_details_method)


@router.callback_query(F.data.startswith('add_payment_details_method|'))
async def add_payment_details_method(call: CallbackQuery, state: AddPaymentDetails.type):
    await call.message.delete()
    method = call.data.split('|')[1]
    await state.update_data(type=method)
    await call.message.answer('Введите номер счета: ')
    await state.set_state(AddPaymentDetails.details)


@router.message(StateFilter(AddPaymentDetails.details))
async def add_payment_details_details(message: Message, state: FSMContext, session: AsyncSession):
    await message.delete()
    account_number = message.text
    data = await state.get_data()
    service = data['service']
    type = data['type']
    try:
        new_payment_details = PaymentDetails(
            service=service,
            type=type,
            account_number=account_number
        )
        session.add(new_payment_details)
        await session.commit()
        await message.answer('Реквизиты успешно добавлены.')
    except Exception as e:
        await session.rollback()  # откат в случае ошибки
        print(f'Error with adding to db: {e}')
        await message.answer('Произошла ошибка при добавлении реквизитов.')
    await state.clear()


@router.callback_query(F.data == 'delete_payment_details')
async def delete_payment_details(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    await call.message.delete()
    await call.message.answer('Напишите ID реквизита для удаления: ')
    await state.set_state(DeletePayment.id)


@router.message(StateFilter(DeletePayment.id))
async def delete_payment_details_id(message: Message, session: AsyncSession, state: FSMContext):
    await message.delete()
    payment_id = message.text
    try:
        await session.execute(delete(PaymentDetails).where(PaymentDetails.id == int(payment_id)))
        await session.commit()
        await message.answer('Реквизиты успешно удалены.')
    except Exception as e:
        await session.rollback()
        print(f'Error with deleting from db: {e}')
        await message.answer('Произошла ошибка при удалении реквизитов.')
    await state.clear()


@router.callback_query(F.data == 'back_to_admin')
async def back_to_admin(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('Открыта админ-панель!', reply_markup=kb.admin_panel)


@router.message(F.text == 'Статистика')
async def statistics(message: Message, user: User):
    if user.tg_id in config.ADMIN_IDS:
        await message.answer('Статистика пока что недоступна.')


@router.message(F.text == 'Рассылка')
async def mailing(message: Message, user: User, state: FSMContext):
    if user.tg_id in config.ADMIN_IDS:
        await message.answer('Напишите сообщение для рассылки ниже:')
        await state.set_state(Mailing.text)


@router.message(StateFilter(Mailing.text))
async def send_message(message: Message, session: AsyncSession, state: FSMContext):
    text = message.text
    users = await session.execute(select(User))
    users = users.scalars().all()
    for user in users:
        try:
            await message.bot.send_message(user.tg_id, text=text)
        except Exception as e:
            print(f'Error with sending message to {user.tg_id}: {e}')


@router.message(F.text == 'Назад')
async def back(message: Message, user: User):
    if user.tg_id in config.ADMIN_IDS:
        await message.answer(text=f'<b>👋 Добро пожаловать администратор, {user.fname}!\n выберите сервис ниже:</b>',
                             parse_mode="HTML", reply_markup=kb.main_admin)
