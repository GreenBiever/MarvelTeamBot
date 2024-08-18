import json
import random
import string
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from nft_bot.keyboards import kb
from nft_bot.databases import requests
from nft_bot.main_handlers.promocode_handlers import CreatePromocode
from nft_bot.states import deposit_state, withdraw_state, admin_items_state, worker_state
from nft_bot import config
from sqlalchemy.ext.asyncio import AsyncSession
from databases.models import User, Promocode, UserPromocodeAssotiation
from sqlalchemy import update, select, delete
from nft_bot.databases.crud import (get_created_promocodes, get_promocode_by_code)

bot: Bot = Bot(config.TOKEN)
router = Router()
languages = ["en", "ru", "pl", "uk"]
translations = {}

for lang in languages:
    with open(f"locales/{lang}.json", "r", encoding="utf-8") as file:
        translations[lang] = json.load(file)


@router.message(F.text == 'Воркер')
async def open_work_panel(message: Message, user: User, session: AsyncSession):
    if user.is_worker:
        await bot.send_message(chat_id=message.from_user.id, text='Ворк-панель: ',
                               parse_mode="HTML", reply_markup=kb.work_panel)
    if not user.is_worker:
        user.is_worker = True
        session.add(user)
        await bot.send_message(chat_id=message.from_user.id, text='Ворк-панель: ',
                               parse_mode="HTML", reply_markup=kb.work_panel)


@router.callback_query(lambda c: c.data == 'work_panel')
async def work_panel(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text='Ворк-панель: ',
                                parse_mode="HTML", reply_markup=kb.work_panel)


@router.callback_query(lambda c: c.data == 'connect_mamont')
async def connect_mamont(call: types.CallbackQuery, state: worker_state.WorkerPanel.mamont_id):
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text='Введите <b>ID</b> лохматого 🦣:', parse_mode="HTML")
    await state.set_state(worker_state.WorkerPanel.mamont_id)


@router.message(StateFilter(worker_state.WorkerPanel.mamont_id))
async def connect_mamont_id(message: types.Message, user: User, state: worker_state.WorkerPanel.mamont_id,
                            session: AsyncSession):
    mamont_id = message.text

    if not mamont_id.isdigit():
        await bot.send_message(chat_id=message.from_user.id, text='Введите корректный mamont_id!', parse_mode="HTML")
        return

    result = await session.execute(select(User).where(User.tg_id == int(mamont_id)))
    user1 = result.scalars().first()

    if not user1:
        await bot.send_message(chat_id=message.from_user.id, text='Такого mamont_id не существует!', parse_mode="HTML")
        return

    elif user1.referer_id is not None:
        await bot.send_message(chat_id=message.from_user.id, text='Этот mamont_id уже привязан!', parse_mode="HTML")
        pass

    else:
        await state.update_data(mamont_id=mamont_id)
        await session.execute(
            update(User)
            .where(User.tg_id == mamont_id)
            .values(referer_id=user.id)
        )
        await state.clear()
        await bot.send_message(chat_id=message.from_user.id, text='Лохматый привязан!', parse_mode="HTML")


@router.callback_query(lambda c: c.data == 'control_mamonts')
async def control_mamonts(call: types.CallbackQuery, user: User, session: AsyncSession,
                          state: worker_state.WorkerMamont.mamont_id):
    result = await session.execute(select(User).where(User.referer_id == user.id))
    users = result.scalars().all()

    if users:
        text = 'Лохматые:\n\n'
        for user in users:
            text += f'ID: {user.tg_id}\n'
        text += '\n<b>Всего лохматых:</b> ' + str(len(users))
        text += '\nВведите ID лохматого ниже для управления: '
    else:
        text = 'У вас нет лохматых.'

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                parse_mode="HTML", reply_markup=kb.back_to_admin)
    await state.set_state(worker_state.WorkerMamont.mamont_id)


@router.message(StateFilter(worker_state.WorkerMamont.mamont_id))
async def mamont_control_panel(message: Message, session: AsyncSession, state: worker_state.WorkerMamont.mamont_id):
    mamont_id = message.text
    mamont_id = message.text

    if not mamont_id.isdigit():
        await bot.send_message(chat_id=message.from_user.id, text='Введите корректный mamont_id!', parse_mode="HTML")
        return

    result = await session.execute(select(User).where(User.tg_id == int(mamont_id)))
    user = result.scalars().first()

    if not user:
        await bot.send_message(chat_id=message.from_user.id, text='Такого mamont_id не существует!', parse_mode="HTML")
        return

    if user.is_buying:
        user_is_buying = 'Покупка включена'
    else:
        user_is_buying = 'Покупка выключена'

    if user.is_withdraw:
        user_is_withdraw = 'Вывод включен'
    else:
        user_is_withdraw = 'Вывод выключен'

    if user.is_verified:
        user_is_verified = 'Верифицирован'
    else:
        user_is_verified = 'Не верифицирован'

    if user.is_blocked:
        user_is_blocked = 'Заблокирован'
    else:
        user_is_blocked = 'Активен'

    keyboard = await kb.create_mamont_control_kb(mamont_id, session)
    text = (f'🏙 <b>Профиль лохматого</b> {mamont_id}\n\n'
            f'<b>Информация</b>\n'
            f'┠ Баланс: <b>{user.balance}</b>\n'
            f'┠ Мин. депозит: <b>{user.min_deposit} RUB</b>\n'
            f'┠ Мин. вывод: <b>{user.min_withdraw} RUB</b>\n'
            f'┠ 🔰 <b>{user_is_buying}</b>\n'
            f'┠ 🔰 <b>{user_is_withdraw}</b>\n'
            f'┠ 🔐 <b>{user_is_blocked}</b>\n'
            f'┖ 🔺 <b>{user_is_verified}</b>\n\n'
            f'<b>Последний логин</b>\n'
            f'┖ {user.last_login}')
    await state.update_data(mamont_id=mamont_id)
    await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith('mamont|'))
async def mamont_control_handler(call: types.CallbackQuery, state: worker_state.WorkerMamont.mamont_id,
                                 session: AsyncSession):
    global new_mamont_deposit, new_mamont_withdraw
    callback = call.data.split('|')[1]
    state_info = await state.get_data()
    mamont_id = state_info['mamont_id']
    result = await session.execute(select(User).where(User.tg_id == int(mamont_id)))
    user = result.scalars().first()
    if callback == 'change_balance':
        await bot.edit_message_text(message_id=call.message.message_id, chat_id=call.from_user.id,
                                    text='Введите сумму для пополнения баланса лохматого: ')
        await state.set_state(worker_state.WorkerMamont.balance_amount)
        return
    elif callback == 'min_deposit':
        min_mamont_deposit = user.min_deposit
        if min_mamont_deposit == 5000:
            new_mamont_deposit = 8000
        elif min_mamont_deposit == 8000:
            new_mamont_deposit = 10000
        elif min_mamont_deposit == 10000:
            new_mamont_deposit = 20000
        elif min_mamont_deposit == 20000:
            new_mamont_deposit = 50000
        elif min_mamont_deposit == 50000:
            new_mamont_deposit = 5000
        await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(min_deposit=new_mamont_deposit))
        await session.commit()
    elif callback == 'min_withdraw':
        min_mamont_withdraw = user.min_withdraw
        if min_mamont_withdraw == 5000:
            new_mamont_withdraw = 8000
        elif min_mamont_withdraw == 8000:
            new_mamont_withdraw = 10000
        elif min_mamont_withdraw == 10000:
            new_mamont_withdraw = 20000
        elif min_mamont_withdraw == 20000:
            new_mamont_withdraw = 50000
        elif min_mamont_withdraw == 50000:
            new_mamont_withdraw = 5000
        await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(min_withdraw=new_mamont_withdraw))
        await session.commit()
    elif callback == 'unverify':
        await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(is_verified=False))
        await session.commit()
    elif callback == 'verify':
        await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(is_verified=True))
        await session.commit()
    elif callback == 'withdraw':
        if user.is_withdraw:
            await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(is_withdraw=False))
            await session.commit()
        else:
            await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(is_withdraw=True))
            await session.commit()
    elif callback == 'buying':
        if user.is_buying:
            await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(is_buying=False))
            await session.commit()
        else:
            await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(is_buying=True))
            await session.commit()
    elif callback == 'block':
        await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(is_blocked=True))
        await session.commit()
    elif callback == 'unblock':
        await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(is_blocked=False))
        await session.commit()
    elif callback == 'delete':
        await session.execute(delete(User).where(User.tg_id == int(mamont_id)))
        await session.commit()
    elif callback == 'update':
        result2 = await session.execute(select(User).where(User.tg_id == int(mamont_id)))
        user = result2.scalars().first()

        if user.is_buying:
            user_is_buying = 'Покупка включена'
        else:
            user_is_buying = 'Покупка выключена'

        if user.is_withdraw:
            user_is_withdraw = 'Вывод включен'
        else:
            user_is_withdraw = 'Вывод выключен'

        if user.is_verified:
            user_is_verified = 'Верифицирован'
        else:
            user_is_verified = 'Не верифицирован'

        if user.is_blocked:
            user_is_blocked = 'Заблокирован'
        else:
            user_is_blocked = 'Активен'

        keyboard = await kb.create_mamont_control_kb(mamont_id, session)
        text = (f'🏙 <b>Профиль лохматого</b> {mamont_id}\n\n'
                f'<b>Информация</b>\n'
                f'┠ Баланс: <b>{user.balance}</b>\n'
                f'┠ Мин. депозит: <b>{user.min_deposit} RUB</b>\n'
                f'┠ Мин. вывод: <b>{user.min_withdraw} RUB</b>\n'
                f'┠ 🔰 <b>{user_is_buying}</b>\n'
                f'┠ 🔰 <b>{user_is_withdraw}</b>\n'
                f'┠ 🔐 <b>{user_is_blocked}</b>\n'
                f'┖ 🔺 <b>{user_is_verified}</b>\n\n'
                f'<b>Последний логин</b>\n'
                f'┖ {user.last_login}')
        await call.answer('Успешно обновлено')
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                    parse_mode="HTML", reply_markup=keyboard)
        return

    result2 = await session.execute(select(User).where(User.tg_id == int(mamont_id)))
    user2 = result2.scalars().first()

    if user2.is_buying:
        user_is_buying = 'Покупка включена'
    else:
        user_is_buying = 'Покупка выключена'

    if user2.is_withdraw:
        user_is_withdraw = 'Вывод включен'
    else:
        user_is_withdraw = 'Вывод выключен'

    if user2.is_verified:
        user_is_verified = 'Верифицирован'
    else:
        user_is_verified = 'Не верифицирован'

    if user2.is_blocked:
        user_is_blocked = 'Заблокирован'
    else:
        user_is_blocked = 'Активен'

    keyboard = await kb.create_mamont_control_kb(mamont_id, session)
    text = (f'🏙 <b>Профиль лохматого</b> {mamont_id}\n\n'
            f'<b>Информация</b>\n'
            f'┠ Баланс: <b>{user2.balance}</b>\n'
            f'┠ Мин. депозит: <b>{user2.min_deposit} RUB</b>\n'
            f'┠ Мин. вывод: <b>{user2.min_withdraw} RUB</b>\n'
            f'┠ 🔰 <b>{user_is_buying}</b>\n'
            f'┠ 🔰 <b>{user_is_withdraw}</b>\n'
            f'┠ 🔐 <b>{user_is_blocked}</b>\n'
            f'┖ 🔺 <b>{user_is_verified}</b>\n\n'
            f'<b>Последний логин</b>\n'
            f'┖ {user2.last_login}')
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                parse_mode="HTML", reply_markup=keyboard)


@router.message(StateFilter(worker_state.WorkerMamont.balance_amount))
async def change_mamont_balance(message: Message, session: AsyncSession,
                                state: worker_state.WorkerMamont.balance_amount):
    await message.delete()
    balance_amount = message.text
    if not balance_amount.isdigit():
        await bot.send_message(chat_id=message.from_user.id, text='Введите корректную сумму!', parse_mode="HTML")
        return
    state_info = await state.get_data()
    mamont_id = state_info['mamont_id']
    await session.execute(update(User).where(User.tg_id == int(mamont_id)).values(balance=int(balance_amount)))
    await session.commit()
    await bot.send_message(chat_id=message.from_user.id, text='Баланс изменен!')
    result = await session.execute(select(User).where(User.tg_id == int(mamont_id)))
    user = result.scalars().first()

    if user.is_buying:
        user_is_buying = 'Покупка включена'
    else:
        user_is_buying = 'Покупка выключена'

    if user.is_withdraw:
        user_is_withdraw = 'Вывод включен'
    else:
        user_is_withdraw = 'Вывод выключен'

    if user.is_verified:
        user_is_verified = 'Верифицирован'
    else:
        user_is_verified = 'Не верифицирован'

    if user.is_blocked:
        user_is_blocked = 'Заблокирован'
    else:
        user_is_blocked = 'Активен'

    keyboard = await kb.create_mamont_control_kb(mamont_id, session)
    text = (f'🏙 <b>Профиль лохматого</b> {mamont_id}\n\n'
            f'<b>Информация</b>\n'
            f'┠ Баланс: <b>{user.balance}</b>\n'
            f'┠ Мин. депозит: <b>{user.min_deposit} RUB</b>\n'
            f'┠ Мин. вывод: <b>{user.min_withdraw} RUB</b>\n'
            f'┠ 🔰 <b>{user_is_buying}</b>\n'
            f'┠ 🔰 <b>{user_is_withdraw}</b>\n'
            f'┠ 🔐 <b>{user_is_blocked}</b>\n'
            f'┖ 🔺 <b>{user_is_verified}</b>\n\n'
            f'<b>Последний логин</b>\n'
            f'┖ {user.last_login}')
    await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data == 'worker_back')
async def cmd_worker_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Привет, воркер!',
                                     reply_markup=kb.work_panel)


@router.callback_query(F.data.startswith('worker_user|'))
async def open_worker(callback: CallbackQuery, user: User, session: AsyncSession, state: worker_state.WorkerMamont.mamont_id):
    mamont_id = callback.data.split('|')[1]
    if not mamont_id.isdigit():
        await bot.send_message(chat_id=callback.from_user.id, text='Введите корректный mamont_id!', parse_mode="HTML")
        return

    result = await session.execute(select(User).where(User.tg_id == int(mamont_id)))
    user = result.scalars().first()

    if not user:
        await bot.send_message(chat_id=callback.from_user.id, text='Такого mamont_id не существует!', parse_mode="HTML")
        return

    if user.is_buying:
        user_is_buying = 'Покупка включена'
    else:
        user_is_buying = 'Покупка выключена'

    if user.is_withdraw:
        user_is_withdraw = 'Вывод включен'
    else:
        user_is_withdraw = 'Вывод выключен'

    if user.is_verified:
        user_is_verified = 'Верифицирован'
    else:
        user_is_verified = 'Не верифицирован'

    if user.is_blocked:
        user_is_blocked = 'Заблокирован'
    else:
        user_is_blocked = 'Активен'

    keyboard = await kb.create_mamont_control_kb(mamont_id, session)
    text = (f'🏙 <b>Профиль лохматого</b> {mamont_id}\n\n'
            f'<b>Информация</b>\n'
            f'┠ Баланс: <b>{user.balance}</b>\n'
            f'┠ Мин. депозит: <b>{user.min_deposit} RUB</b>\n'
            f'┠ Мин. вывод: <b>{user.min_withdraw} RUB</b>\n'
            f'┠ 🔰 <b>{user_is_buying}</b>\n'
            f'┠ 🔰 <b>{user_is_withdraw}</b>\n'
            f'┠ 🔐 <b>{user_is_blocked}</b>\n'
            f'┖ 🔺 <b>{user_is_verified}</b>\n\n'
            f'<b>Последний логин</b>\n'
            f'┖ {user.last_login}')
    await state.update_data(mamont_id=mamont_id)
    await bot.send_message(chat_id=callback.from_user.id, text=text, parse_mode="HTML", reply_markup=keyboard)

##
# <Promocodes>
###

@router.callback_query(F.data == 'worker_promocode')
async def get_promocode_menu(cb: CallbackQuery):
    await cb.message.edit_text("Выберите действие с промокодами:",
                               reply_markup=kb.get_promocode_menu_kb())


@router.callback_query(F.data == 'create_promocode')
async def cmd_create_promocode(cb: CallbackQuery, state: FSMContext):
    await state.set_state(CreatePromocode.wait_code)
    await cb.message.edit_text("✍️ Укажите новый промокод::",
                               reply_markup=kb.get_worker_menu_back_kb())


@router.message(F.text, CreatePromocode.wait_code)
async def set_promocode_code(message: Message, state: FSMContext, session: AsyncSession):
    allowed_char_range = string.ascii_uppercase + string.digits
    if (not all(char in allowed_char_range for char in message.text)
        or len(message.text)) <= 4:
        await message.answer('Используйте только большие англ. буквы и цифры, длина промокода больше 4 символов:',
                             reply_markup=kb.get_worker_menu_back_kb())
        return
    if await get_promocode_by_code(session, message.text) is not None:
        await message.answer('Промокод с таким кодом уже существует, введите другой код:',
                             reply_markup=kb.get_worker_menu_back_kb())
        return
    await state.update_data(code=message.text)
    await state.set_state(CreatePromocode.wait_amount)
    await message.answer("Введите сумму, которая будет получена при активации промокода(в USD):",
                         reply_markup=kb.get_worker_menu_back_kb())


@router.message(F.text, CreatePromocode.wait_amount)
async def set_promocode_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Сумма должна быть числом, введите ещё раз:",
                             reply_markup=kb.get_worker_menu_back_kb())
        return
    await state.update_data(amount=amount)
    await state.set_state(CreatePromocode.wait_type)
    await message.answer("Выберите тип промокода - введите '0' для одноразового или '1' для многоразового:",
                         reply_markup=kb.get_worker_menu_back_kb())


@router.message(F.text, CreatePromocode.wait_type)
async def set_promocode_type(message: Message, state: FSMContext, user: User,
                             session: AsyncSession):
    if message.text not in ('1', '0'):
        await message.answer(
            "Выберите тип промокода - введите '0' для одноразового или '1' для многоразового:",
            reply_markup=kb.get_worker_menu_back_kb())
        return
    data = await state.get_data()
    await state.clear()
    promocode = Promocode(code=data['code'],
                          amount=data['amount'],
                          reusable=True if message.text == '1' else False)
    (await promocode.awaitable_attrs.users).append(
        UserPromocodeAssotiation(user=user, is_creator=True))
    session.add(promocode)
    await message.answer("Промокод успешно создан", reply_markup=kb.get_worker_menu_back_kb())


@router.callback_query(F.data == 'get_promocode_list')
async def cmd_get_promocode_list(cb: CallbackQuery, user: User, session: AsyncSession):
    await cb.message.edit_text("Выберите промокод",
                               reply_markup=kb.get_promocode_list_kb(
                                   await get_created_promocodes(session, user),
                               ))


@router.callback_query(F.data.startswith('manage_promocode_'))
async def cmd_manage_promocode(cb: CallbackQuery, user: User, session: AsyncSession):
    promocode = await session.get(Promocode, cb.data.split('_')[-1])
    await cb.message.edit_text(f'''Промокод <code>{promocode.code}</code>
Сумма: <b>{promocode.amount} USD</b>
Тип: {'Многоразовый' if promocode.reusable else 'Одноразовый'}''',
                               reply_markup=kb.get_promocode_managment_kb(promocode))


@router.callback_query(F.data.startswith('delete_promocode_'))
async def cmd_delete_promocode(cb: CallbackQuery, session: AsyncSession):
    promocode = await session.get(Promocode, cb.data.split('_')[-1])
    await session.delete(promocode)
    await cb.message.edit_text(f"Промокод <code>{promocode.code}</code> удалён!",
                               reply_markup=kb.get_worker_menu_back_kb())

###
# </Promocodes>
###
