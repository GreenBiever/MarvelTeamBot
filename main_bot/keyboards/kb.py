from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


main_kb = [
    [KeyboardButton(text="💎 Профиль"),
     KeyboardButton(text="💼 Трейд бот")],
    [KeyboardButton(text='🎆 NFT бот'),
     KeyboardButton(text='🗽 О проекте')]
]

admin_kb = [
    [KeyboardButton(text="💎 Профиль"),
     KeyboardButton(text="💼 Трейд бот")],
    [KeyboardButton(text='🎆 NFT бот'),
     KeyboardButton(text='🗽 О проекте')],
    [KeyboardButton(text='🧐 Админ панель')]
]

main = ReplyKeyboardMarkup(keyboard=main_kb, resize_keyboard=True)
main_admin = ReplyKeyboardMarkup(keyboard=admin_kb, resize_keyboard=True)

admin_panel_kb = [
    [KeyboardButton(text='Пользователи'),
     KeyboardButton(text='Реквизиты')],
    [KeyboardButton(text='Статистика')],
    [KeyboardButton(text='Назад')]
]

admin_panel = ReplyKeyboardMarkup(keyboard=admin_panel_kb, resize_keyboard=True)


services_details_kb = [
    [InlineKeyboardButton(text='💼 Трейд бот', callback_data='details_service|1')],
    [InlineKeyboardButton(text='🎆 NFT бот', callback_data='details_service|2')]
]

services_details = InlineKeyboardMarkup(inline_keyboard=services_details_kb)


apply_kb = [
    [InlineKeyboardButton(text='Подать заявку', callback_data='apply')]
]

apply = InlineKeyboardMarkup(inline_keyboard=apply_kb)

application_send_kb = [
    [InlineKeyboardButton(text='Отправить', callback_data='send_application'),
     InlineKeyboardButton(text='Заново', callback_data='again')]
]

application_send = InlineKeyboardMarkup(inline_keyboard=application_send_kb)

def get_admin_accept_kb(user_id: int):
    admin_accept_kb = [
        [InlineKeyboardButton(text='✅ Принять', callback_data=f'request_accept_{user_id}'),
         InlineKeyboardButton(text='❌ Отклонить', callback_data=f'request_decline_{user_id}')]
    ]

    admin_accept = InlineKeyboardMarkup(inline_keyboard=admin_accept_kb)
    return admin_accept