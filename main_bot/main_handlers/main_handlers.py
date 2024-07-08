from aiogram.filters import StateFilter
from aiogram import F, Router
from databases import db
import config
from aiogram.types import Message, FSInputFile
from aiogram import types, Bot
from keyboards import kb
from services.images import image_generator
from states import application_state

router = Router()



@router.message(F.text == '/start')
async def cmd_start(message: Message, bot: Bot):
    user = await db.cmd_start_db(message.from_user.id, message.from_user.username)
    print(user)
    if user:
        ADMIN_ID = config.ADMIN_ID
        ADMIN_ID_LIST = [int(admin_id) for admin_id in ADMIN_ID.split(",")]
        status = await db.get_user_status(message.from_user.id)
        if status == "blocked":
            await message.answer('Вы заблокированы!')
        else:
            await bot.send_message(message.from_user.id,
                                   text=f'<b>👋Добро пожаловать, {message.from_user.first_name} выберите сервис ниже:</b>',
                                   parse_mode="HTML", reply_markup=kb.main)
            if message.from_user.id in ADMIN_ID_LIST:
                await message.answer(f'Вы авторизовались как администратор!', reply_markup=kb.main_admin)
    else:
        await bot.send_message(message.from_user.id,
                               text=f'<b>👋Добро пожаловать, {message.from_user.first_name} Подай заявку чтобы присоединиться к 💎Parimatch Team💎</b>',
                               parse_mode="HTML", reply_markup=kb.apply)


@router.callback_query(lambda call: call.data == 'apply')
async def application_start(call: types.CallbackQuery, 
                            state: application_state.Application.first_question,
                            bot: Bot):
    if call.data == 'apply':
        await bot.send_message(call.from_user.id, text='<b>Твоя заявка: Не заполнена\n\n'
                                                       '1. ---\n'
                                                       '2. ---\n'
                                                       '3. ---\n\n'
                                                       '🕵️ Откуда вы о нас узнали?</b>', parse_mode='HTML')
        await state.set_state(application_state.Application.first_question)


@router.message(StateFilter(application_state.Application.first_question))
async def application_fist(message: Message, 
                           state: application_state.Application.first_question,
                           bot: Bot):
    answer = message.text
    await state.update_data(first_question=answer)
    await bot.send_message(message.from_user.id, text='<b>Твоя заявка: Не заполнена\n\n'
                                                      f'1. {answer}\n'
                                                      '2. ---\n'
                                                      '3. ---\n\n'
                                                      '🧠 Есть ли опыт работы? Если да то какой?</b>', parse_mode='HTML')
    await state.set_state(application_state.Application.second_question)


@router.message(StateFilter(application_state.Application.second_question))
async def application_second(message: Message, 
                             state: application_state.Application.first_question,
                             bot: Bot):
    answer = message.text
    state_info = await state.get_data()
    first_answer = state_info.get('first_question')
    await state.update_data(second_question=answer)
    await bot.send_message(message.from_user.id, text='<b>Твоя заявка: Не заполнена\n\n'
                                                      f'1. {first_answer}\n'
                                                      f'2. {answer}\n'
                                                      '3. ---\n\n'
                                                      '🧑‍💻 Сколько времени готовы уделять работе?</b>',
                           parse_mode='HTML')
    await state.set_state(application_state.Application.third_question)


@router.message(StateFilter(application_state.Application.third_question))
async def application_third(message: Message,
                             state: application_state.Application.third_question,
                             bot: Bot):
    answer = message.text
    state_info = await state.get_data()
    first_answer = state_info.get('first_question')
    second_answer = state_info.get('second_question')
    await state.update_data(user_name=message.from_user.username)
    await state.update_data(user_id=message.from_user.id)
    await state.update_data(third_question=answer)
    await bot.send_message(message.from_user.id, text='<b>Твоя заявка: Заполнена\n\n'
                                                      f'1. {first_answer}\n'
                                                      f'2. {second_answer}\n'
                                                      f'3. {answer}\n\n'
                                                      '🧑Отправить?</b>', parse_mode='HTML',
                           reply_markup=kb.application_send)


@router.callback_query(lambda call: call.data in ['send_application', 'again'])
async def application_send(call: types.CallbackQuery,
                            state: application_state.Application.first_question,
                            bot: Bot):
    if call.data == 'send_application':
        state_info = await state.get_data()
        first_answer = state_info.get('first_question')
        second_answer = state_info.get('second_question')
        third_answer = state_info.get('third_question')
        application_username = state_info.get('user_name')
        ADMIN_ID = config.ADMIN_ID
        ADMIN_ID_LIST = [int(admin_id) for admin_id in ADMIN_ID.split(",")]
        for admin in ADMIN_ID_LIST:
            await bot.send_message(admin, text='Уважаемый администратор'
                                               '\nОтправлена новая заявка на работу!!!\n\n'
                                               f'<b>Имя пользователя:</b> <code>@{application_username}</code>\n'
                                               f'<b>Первый ответ: {first_answer}</b>\n'
                                               f'<b>Второй ответ: {second_answer}</b>\n'
                                               f'<b>Третий ответ: {third_answer}</b>', parse_mode='HTML',
                                   reply_markup=kb.admin_accept)
    elif call.data == 'again':
        await state.clear()
        await bot.send_message(call.from_user.id,
                               text=f'<b>👋Добро пожаловать, {call.from_user.first_name} Подай заявку чтобы присоединиться к 💎Parimatch Team💎</b>',
                               parse_mode="HTML", reply_markup=kb.apply)


@router.callback_query(lambda call: call.data in ['accept', 'deny'])
async def admin_application(call: types, state: application_state.Application.user_id,
                            bot: Bot):
    state_info = await state.get_data()
    application_username = state_info.get('user_name')
    application_user_id = state_info.get('user_id')
    if call.data == 'accept':
        await db.add_user(application_user_id, application_username)
        await bot.send_message(application_user_id, text='✅ Ваша заявка принята\n\n'
                                                         'Напишите /start заново!!!', reply_markup=kb.main)
    elif call.data == 'deny':
        await bot.send_message(application_user_id, text='✅ Ваша заявка отклонена', reply_markup=kb.main)
        await bot.send_message(application_user_id,
                               text=f'<b>👋Добро пожаловать, {call.from_user.first_name} Подай заявку чтобы присоединиться к 💎Parimatch Team💎</b>',
                               parse_mode="HTML", reply_markup=kb.apply)





@router.message(F.text == '💎 Профиль')
async def profile(message: Message, bot: Bot):
    data = ['BRONZE', '2', '0', '0', '25000']
    image = image_generator.generate_image(data)
    image_path = FSInputFile(image)
    await bot.send_photo(message.from_user.id, photo=image_path, caption='<b>🔮 Профиль воркера</b>', parse_mode='HTML')
