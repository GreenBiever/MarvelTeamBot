import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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


def create_profile_kb(lang):
    buttons = translations[lang]["buttons"].get('profile_kb', {})
    profile_kb = [
        [InlineKeyboardButton(text=buttons['wallet'], callback_data='wallet')],
        [InlineKeyboardButton(text=buttons['verification'], callback_data='verification'),
         InlineKeyboardButton(text=buttons['favorites'], callback_data='favorites')],
        [InlineKeyboardButton(text=buttons['statistics'], callback_data='statistics'),
         InlineKeyboardButton(text=buttons['settings'], callback_data='settings')],
        [InlineKeyboardButton(text=buttons['my_nft'], callback_data='my_nft'),
         InlineKeyboardButton(text=buttons['agreement'], callback_data='agreement')],
        [InlineKeyboardButton(text=buttons['how_to_create_nft'], callback_data='how_to_create_nft')]
    ]

    profile = InlineKeyboardMarkup(row_width=2, inline_keyboard=profile_kb)
    return profile


def create_wallet_kb(lang):
    buttons = translations[lang]["buttons"].get('wallet_kb', {})
    wallet_kb = [
        [InlineKeyboardButton(text=buttons['top_up'], callback_data='top_up'),
         InlineKeyboardButton(text=buttons['withdraw'], callback_data='withdraw')],
        [InlineKeyboardButton(text=buttons['promocode'], callback_data='promocode')],
        [InlineKeyboardButton(text='⬅️', callback_data='back')]
    ]

    wallet = InlineKeyboardMarkup(inline_keyboard=wallet_kb)
    return wallet


def create_verification_kb(lang):
    buttons = translations[lang]["buttons"].get('verification_kb', {})
    verification_kb = [
        [InlineKeyboardButton(text=buttons['verify'], callback_data='verify')],
        [InlineKeyboardButton(text='⬅️', callback_data='back')]
    ]

    verification = InlineKeyboardMarkup(inline_keyboard=verification_kb)
    return verification


def create_favourites_kb(lang):
    buttons = translations[lang]["buttons"].get('favourites_kb', {})
    favourites_kb = [
        [InlineKeyboardButton(text="⬅️", callback_data='left'),
         InlineKeyboardButton(text="0/0", callback_data='zero'),
         InlineKeyboardButton(text='➡️️', callback_data='right')],
        [InlineKeyboardButton(text='⬅️', callback_data='back')]
    ]

    favourites = InlineKeyboardMarkup(inline_keyboard=favourites_kb)
    return favourites
