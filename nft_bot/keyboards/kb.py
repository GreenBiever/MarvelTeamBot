from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from nft_bot.databases import db

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

main = ReplyKeyboardMarkup(keyboard=main_kb, resize_keyboard=True, input_field_placeholder='Выберите пункт ниже')

language_kb = [
    [InlineKeyboardButton(text='🇷🇺 Русский', callback_data='ru'),
     InlineKeyboardButton(text='🇬🇧 English', callback_data='en')],
    [InlineKeyboardButton(text='🇵🇱 Polski', callback_data='pl'),
     InlineKeyboardButton(text='🇺🇦 Український', callback_data='uk')]
]

language = InlineKeyboardMarkup(inline_keyboard=language_kb)