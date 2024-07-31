import json
import random
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, FSInputFile
from nft_bot.keyboards import kb
from nft_bot.databases import requests
from nft_bot.states import deposit_state, withdraw_state, admin_items_state, worker_state
from nft_bot import config
from sqlalchemy.ext.asyncio import AsyncSession
from nft_bot.databases.models import User
from sqlalchemy import update, select

bot: Bot = Bot(config.TOKEN)
router = Router()
ADMIN_ID = config.ADMIN_ID
ADMIN_ID_LIST = [int(admin_id) for admin_id in ADMIN_ID.split(",")]
languages = ["en", "ru", "pl", "uk"]
translations = {}

for lang in languages:
    with open(f"locales/{lang}.json", "r", encoding="utf-8") as file:
        translations[lang] = json.load(file)


# Функция для получения перевода
def get_translation(lang, key, **kwargs):
    translation = translations[lang].get(key, key)
    if isinstance(translation, dict):
        translation = translation.get(kwargs['status'], kwargs['status'])
    return translation.format(**kwargs)


"""
Callback handlers for Admin functionality
"""


@router.message(F.text == 'Админ-панель')
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMIN_ID_LIST:
        await bot.send_message(message.from_user.id, text='Вы вошли в админ-панель!', parse_mode="HTML",
                               reply_markup=kb.admin_panel)


@router.callback_query(lambda c: c.data == 'add_category')
async def add_category(call: types.CallbackQuery, state: admin_items_state.AdminCategoriesItems.category):
    await call.message.answer(text='Введите название категории (коллекции NFT):', parse_mode="HTML")
    await state.set_state(admin_items_state.AdminCategoriesItems.category)


@router.message(StateFilter(admin_items_state.AdminCategoriesItems.category))
async def add_category_name(message: types.Message, state: admin_items_state.AdminCategoriesItems.category,
                            session: AsyncSession):
    category_name = message.text
    await state.clear()
    await requests.add_category(session, category_name)
    await message.answer(text='Категория добавлена!', parse_mode="HTML")


@router.callback_query(lambda c: c.data == 'add_item')
async def add_item(call: types.CallbackQuery, state: admin_items_state.AdminCategoriesItems.item,
                   session: AsyncSession):
    categories_keyboard = await kb.get_categories_kb(session)
    await call.message.answer(text='Выберите категорию:', parse_mode="HTML", reply_markup=categories_keyboard)
    await state.set_state(admin_items_state.AdminCategoriesItems.item)


@router.callback_query(lambda c: c.data.startswith('category_'))
async def add_item_to_category(call: types.CallbackQuery, state: admin_items_state.AdminCategoriesItems.item):
    category_id = call.data.split('_')[1]
    await state.update_data(category_id=category_id)
    await call.message.answer(text='Введите название NFT:', parse_mode="HTML")
    await state.set_state(admin_items_state.AdminItems.item_name)


@router.message(StateFilter(admin_items_state.AdminItems.item_name))
async def add_item_name(message: types.Message, state: admin_items_state.AdminItems.item_name):
    item_name = message.text
    await state.update_data(item_name=item_name)
    await message.answer(text='Введите описание NFT (Если описания нет, введите "0")', parse_mode="HTML")
    await state.set_state(admin_items_state.AdminItems.item_description)


@router.message(StateFilter(admin_items_state.AdminItems.item_description))
async def add_item_description(message: types.Message, state: admin_items_state.AdminItems.item_description):
    item_description = message.text
    if item_description == '0':
        item_description = 'Описание отсутствует'
    await state.update_data(item_description=item_description)
    await message.answer(text='Введите цену NFT в долларах $:', parse_mode="HTML")
    await state.set_state(admin_items_state.AdminItems.item_price)


@router.message(StateFilter(admin_items_state.AdminItems.item_price))
async def add_item_price(message: types.Message, state: admin_items_state.AdminItems.item_price):
    item_price = message.text
    await state.update_data(item_price=item_price)
    await message.answer(text='Введите автора NFT:', parse_mode="HTML")
    await state.set_state(admin_items_state.AdminItems.item_author)


@router.message(StateFilter(admin_items_state.AdminItems.item_author))
async def add_item_author(message: types.Message, state: admin_items_state.AdminItems.item_author):
    item_author = message.text
    await state.update_data(item_author=item_author)
    await message.answer(text='Отправьте фото NFT:', parse_mode="HTML")
    await state.set_state(admin_items_state.AdminItems.item_photo)


@router.message(StateFilter(admin_items_state.AdminItems.item_photo))
async def add_item_photo(message: types.Message, state: admin_items_state.AdminItems.item_photo, session: AsyncSession):
    item_photo = message.text
    data = await state.get_data()
    category_id = data.get('category_id')
    print(category_id)
    item_name = data.get('item_name')
    item_description = data.get('item_description')
    item_price = data.get('item_price')
    item_author = data.get('item_author')
    await requests.add_item(session, item_name, item_description, item_price, item_author, item_photo, category_id)
    await message.answer(text='NFT добавлен!', parse_mode="HTML")
    await state.clear()


@router.callback_query(lambda c: c.data == 'delete_category')
async def delete_category(call: types.CallbackQuery, state: admin_items_state.AdminCategoriesItems.category,
                          session: AsyncSession):
    categories_keyboard = await kb.get_categories_kb2(session)
    await call.message.answer(text='Выберите категорию для удаления:', parse_mode="HTML",
                              reply_markup=categories_keyboard)


@router.callback_query(lambda c: c.data.startswith('delete_category_'))
async def delete_category_callback(call: types.CallbackQuery, session: AsyncSession):
    category_id = call.data.split('_')[2]
    await requests.delete_category(session, int(category_id))
    await call.message.answer(text='Категория удалена!', parse_mode="HTML")


@router.callback_query(lambda c: c.data == 'delete_item')
async def delete_item(call: types.CallbackQuery, state: admin_items_state.AdminCategoriesItems.item,
                      session: AsyncSession):
    items_keyboard = await kb.get_delete_items_kb(session)
    await call.message.answer(text='Выберите NFT для удаления:', parse_mode="HTML", reply_markup=items_keyboard)


@router.callback_query(lambda c: c.data.startswith('delete_item_'))
async def delete_item_callback(call: types.CallbackQuery, session: AsyncSession):
    item_id = call.data.split('_')[2]
    await requests.delete_item(session, int(item_id))
    await call.message.answer(text='NFT удален!', parse_mode="HTML")


@router.callback_query(lambda c: c.data == 'work_panel')
async def edit_item(call: types.CallbackQuery):
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
    user = result.scalars().first()

    if not user:
        await bot.send_message(chat_id=message.from_user.id, text='Такого mamont_id не существует!', parse_mode="HTML")
        return

    elif user.referer_id is not None:
        await bot.send_message(chat_id=message.from_user.id, text='Этот mamont_id уже привязан!', parse_mode="HTML")
        pass

    else:
        await state.update_data(mamont_id=mamont_id)
        await session.execute(
            update(User)
            .where(User.tg_id == mamont_id)
            .values(referer_id=message.from_user.id)
        )
        await state.clear()
        await bot.send_message(chat_id=message.from_user.id, text='Лохматый привязан!', parse_mode="HTML")


@router.callback_query(lambda c: c.data == 'control_mamonts')
async def control_mamonts(call: types.CallbackQuery, session: AsyncSession, state: worker_state.WorkerMamont.mamont_id):
    result = await session.execute(select(User).where(User.referer_id == call.from_user.id))
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


@router.callback_query(lambda c: c.data == 'back_to_admin')
async def back_to_admin(call: types.CallbackQuery, user: User):
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text='Админ-панель: ',
                                parse_mode="HTML", reply_markup=kb.admin_panel)


@router.callback_query(lambda c: c.data == 'back_to_admin2')
async def back_to_admin2(call: types.CallbackQuery, user: User):
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text='Ворк-панель: ',
                                parse_mode="HTML", reply_markup=kb.work_panel)


@router.message(StateFilter(worker_state.WorkerMamont.mamont_id))
async def mamont_control_panel(message: Message, session: AsyncSession):
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

    keyboard = await kb.create_mamont_control_kb(mamont_id, session)
    text = (f'🏙 <b>Профиль лохматого</b> {mamont_id}\n\n'
            f'<b>Информация</b>\n'
            f'┠ Баланс: <b>{user.balance}</b>\n'
            f'┠ Мин. депозит: <b>{user.min_deposit} RUB</b>\n'
            f'┠ Мин. вывод: <b>{user.min_withdraw} RUB</b>\n'
            f'┠ 🔰 <b>{user_is_buying}</b>\n'
            f'┠ 🔰 <b>{user_is_withdraw}</b>\n'
            f'┖ 🔺 <b>{user_is_verified}</b>\n\n'
            f'<b>Последний логин</b>\n'
            f'┖ {user.last_login}')
    await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode="HTML", reply_markup=keyboard)