from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database import db

main_kb = [
    [KeyboardButton(text="💎 Профиль")],
    [KeyboardButton(text="🏙 NFT - бот"),
     KeyboardButton(text="🌆 NFT - сайт"),
     KeyboardButton(text="📢 Арбитраж - бот")],
    [KeyboardButton(text="📣 Арбитраж - сайт"),
     KeyboardButton(text='🎰 Игровой - бот'),
     KeyboardButton(text='📉 Трейд - бот')],
    [KeyboardButton(text="📊 Трейд - сайт"),
     KeyboardButton(text='🔎 BTC Поиск - бот'),
     KeyboardButton(text='🌐 Обменник - сайт')],
    [KeyboardButton(text='🗽 О проекте')]
]

admin_kb = [
    [KeyboardButton(text="💎 Профиль")],
    [KeyboardButton(text="🏙 NFT - бот"),
     KeyboardButton(text="🌆 NFT - сайт"),
     KeyboardButton(text="📢 Арбитраж - бот")],
    [KeyboardButton(text="📣 Арбитраж - сайт"),
     KeyboardButton(text='🎰 Игровой - бот'),
     KeyboardButton(text='📉 Трейд - бот')],
    [KeyboardButton(text="📊 Трейд - сайт"),
     KeyboardButton(text='🔎 BTC Поиск - бот'),
     KeyboardButton(text='🌐 Обменник - сайт')],
    [KeyboardButton(text='🗽 О проекте')]
]

main = ReplyKeyboardMarkup(keyboard=main_kb, resize_keyboard=True, input_field_placeholder='Выберите пункт ниже')
main_admin = ReplyKeyboardMarkup(keyboard=admin_kb, resize_keyboard=True, input_field_placeholder='Выберите пункт ниже')


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