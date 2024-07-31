import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select

from nft_bot import config
from nft_bot.databases import requests
from sqlalchemy.ext.asyncio import AsyncSession

from nft_bot.databases.models import User

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


def create_main_kb(lang):
    buttons = translations[lang]["buttons"].get('main_kb', {})
    main_kb = [
        [KeyboardButton(text='🎆 NFT')],
        [KeyboardButton(text=buttons['profile_main'])],
        [KeyboardButton(text=buttons['information_main']),
         KeyboardButton(text=buttons['support_main'])]
    ]
    main = ReplyKeyboardMarkup(keyboard=main_kb, resize_keyboard=True)

    return main


def create_admin_main_kb(lang):
    buttons = translations[lang]["buttons"].get('main_kb', {})
    admin_main_kb = [
        [KeyboardButton(text='🎆 NFT')],
        [KeyboardButton(text=buttons['profile_main'])],
        [KeyboardButton(text=buttons['information_main']),
         KeyboardButton(text=buttons['support_main'])],
        [KeyboardButton(text='Админ-панель')]
    ]
    admin_main = ReplyKeyboardMarkup(keyboard=admin_main_kb, resize_keyboard=True)

    return admin_main


admin_panel_kb = [
    [InlineKeyboardButton(text='Ворк-панель', callback_data='work_panel')],
    [InlineKeyboardButton(text='Добавить категорию', callback_data='add_category'),
     InlineKeyboardButton(text='Добавить товар', callback_data='add_item')],
    [InlineKeyboardButton(text='Удалить категорию', callback_data='delete_category'),
     InlineKeyboardButton(text='Удалить товар', callback_data='delete_item')],
]

admin_panel = InlineKeyboardMarkup(inline_keyboard=admin_panel_kb)


work_panel_kb = [
    [InlineKeyboardButton(text='Привязать по ID', callback_data='connect_mamont')],
    [InlineKeyboardButton(text='Управление 🦣', callback_data='control_mamonts')],
    [InlineKeyboardButton(text='⬅️', callback_data='back_to_admin')]
]

work_panel = InlineKeyboardMarkup(inline_keyboard=work_panel_kb)

back_to_admin_button = InlineKeyboardButton(text='⬅️', callback_data='back_to_admin2')
back_to_admin = InlineKeyboardMarkup(inline_keyboard=[[back_to_admin_button]])

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
         InlineKeyboardButton(text=buttons['agreement'], url=config.AGREEMENT_URL)],
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
        [InlineKeyboardButton(text=buttons['verify'], url=config.SUPPORT_URL)],
        [InlineKeyboardButton(text='⬅️', callback_data='back')]
    ]

    verification = InlineKeyboardMarkup(inline_keyboard=verification_kb)
    return verification


def create_favourites_kb():
    favourites_kb = [
        [InlineKeyboardButton(text="⬅️", callback_data='left'),
         InlineKeyboardButton(text="0/0", callback_data='zero'),
         InlineKeyboardButton(text='➡️️', callback_data='right')],
        [InlineKeyboardButton(text='⬅️', callback_data='back')]
    ]

    favourites = InlineKeyboardMarkup(inline_keyboard=favourites_kb)
    return favourites


def create_statistics_kb():
    statistics_kb = [
        [InlineKeyboardButton(text='⬅️', callback_data='back')]
    ]
    statistics = InlineKeyboardMarkup(inline_keyboard=statistics_kb)
    return statistics


def create_settings_kb(lang):
    buttons = translations[lang]["buttons"].get('settings_kb', {})
    settings_kb = [
        [InlineKeyboardButton(text=buttons['language'], callback_data='language')],
        [InlineKeyboardButton(text=buttons['currency'], callback_data='currency')],
        [InlineKeyboardButton(text='⬅️️', callback_data='back')]
    ]

    settings = InlineKeyboardMarkup(inline_keyboard=settings_kb)
    return settings


def create_nft_kb():
    nft_kb = [
        [InlineKeyboardButton(text='⬅️️', callback_data='back')]
    ]
    nft = InlineKeyboardMarkup(inline_keyboard=nft_kb)
    return nft


def create_deposit_kb(lang):
    buttons = translations[lang]["buttons"].get('deposit_kb', {})
    deposit_kb = [
        [InlineKeyboardButton(text=buttons['card'], callback_data='card'),
         InlineKeyboardButton(text=buttons['crypto'], callback_data='crypto')],
        [InlineKeyboardButton(text='⬅️️', callback_data='back_wallet')]
    ]

    deposit = InlineKeyboardMarkup(inline_keyboard=deposit_kb)
    return deposit


withdraw_kb = [
    [InlineKeyboardButton(text='⬅️️', callback_data='back_wallet')]
]

withdraw = InlineKeyboardMarkup(inline_keyboard=withdraw_kb)

deposit_card_back_kb = [
    [InlineKeyboardButton(text='⬅️️️️', callback_data='back_wallet2')]
]

deposit_card_back = InlineKeyboardMarkup(inline_keyboard=deposit_card_back_kb)

deposit_crypto_kb = [
    [InlineKeyboardButton(text='USDT [TRC-20]', callback_data='usdt')],
    [InlineKeyboardButton(text='BTC', callback_data='btc')],
    [InlineKeyboardButton(text='ETH', callback_data='eth')],
    [InlineKeyboardButton(text='⬅️️️️', callback_data='back_wallet2')]
]

deposit_crypto = InlineKeyboardMarkup(inline_keyboard=deposit_crypto_kb)


def create_card_crypto_kb(lang):
    buttons = translations[lang]["buttons"].get('deposit_top_up_kb', {})
    deposit_kb = [
        [InlineKeyboardButton(text=buttons['check'], callback_data='check_payment')],
        [InlineKeyboardButton(text=buttons['support'], url=config.SUPPORT_URL)],
    ]

    deposit = InlineKeyboardMarkup(inline_keyboard=deposit_kb)
    return deposit


settings_language_kb = [
    [InlineKeyboardButton(text='🇷🇺 Русский', callback_data='set_ru'),
     InlineKeyboardButton(text='🇬🇧 English', callback_data='set_en')],
    [InlineKeyboardButton(text='🇵🇱 Polski', callback_data='set_pl'),
     InlineKeyboardButton(text='🇺🇦 Український', callback_data='set_uk')],
    [InlineKeyboardButton(text='⬅️️', callback_data='back')]
]

settings_language = InlineKeyboardMarkup(inline_keyboard=settings_language_kb)


settings_currency_kb = [
    [InlineKeyboardButton(text='🇺🇦 UAH', callback_data='usd'),
     InlineKeyboardButton(text='🇪🇺 EUR', callback_data='eur')],
    [InlineKeyboardButton(text='🇵🇱 PLN', callback_data='pln'),
     InlineKeyboardButton(text='🇷🇺 RUB', callback_data='rub')],
    [InlineKeyboardButton(text='🇧🇾 BYN', callback_data='byn')],
    [InlineKeyboardButton(text='⬅️️', callback_data='back')]
]

settings_currency = InlineKeyboardMarkup(inline_keyboard=settings_currency_kb)


async def get_categories_kb(session: AsyncSession):
    categories = await requests.get_categories(session)
    categories_kb = [
        [InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}')] for category in categories
    ]

    categories = InlineKeyboardMarkup(inline_keyboard=categories_kb)
    return categories


async def get_categories_kb2(session: AsyncSession):
    categories = await requests.get_categories(session)
    categories_kb = [
        [InlineKeyboardButton(text=category.name, callback_data=f'delete_category_{category.id}')] for category in categories
    ]

    categories = InlineKeyboardMarkup(inline_keyboard=categories_kb)
    return categories


async def get_delete_items_kb(session: AsyncSession):
    items = await requests.get_items(session)
    items_kb = [
        [InlineKeyboardButton(text=item.name, callback_data=f'delete_item_{item.id}')] for item in items
    ]

    items = InlineKeyboardMarkup(inline_keyboard=items_kb)
    return items


async def create_collections_keyboard(session: AsyncSession):
    categories_with_count = await requests.get_categories_with_item_count(session)
    categories_kb = [
        [InlineKeyboardButton(text=f"{category.name} ({category.item_count})",
                              callback_data=f'collection_{category.id}')]
        for category in categories_with_count
    ]
    navigation_buttons = [
        InlineKeyboardButton(text="⬅️", callback_data='left'),
        InlineKeyboardButton(text="1/1", callback_data='zero'),
        InlineKeyboardButton(text='➡️️', callback_data='right')
    ]
    categories_kb.append(navigation_buttons)

    categories_markup = InlineKeyboardMarkup(inline_keyboard=categories_kb)
    return categories_markup


async def create_items_keyboard(category_id, session: AsyncSession):
    items = await requests.get_items_by_category_id(session, category_id)
    items_kb = [
        [InlineKeyboardButton(text=item.name, callback_data=f'token_{item.id}')] for item in items
    ]
    navigation_buttons = [
        InlineKeyboardButton(text="⬅️", callback_data='left'),
        InlineKeyboardButton(text="1/1", callback_data='zero'),
        InlineKeyboardButton(text='➡️️', callback_data='right')
    ]
    items_kb.append(navigation_buttons)

    items_markup = InlineKeyboardMarkup(inline_keyboard=items_kb)
    return items_markup


async def create_buy_keyboard(lang, item_id):
    buttons = translations[lang]["buttons"].get('catalog_kb', {})

    buy_kb = [
        [InlineKeyboardButton(text=buttons['buy'], callback_data=f'buy_{item_id}')],
        [InlineKeyboardButton(text='🤍️', callback_data='add_to_favourites')],
        [InlineKeyboardButton(text='⬅️', callback_data='back_to_catalog')]
    ]

    buy = InlineKeyboardMarkup(inline_keyboard=buy_kb)
    return buy


async def create_mamont_control_kb(mamont_id, session):
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
        user_is_verified = 'Не вериф'
        call_is_verified = 'unverify'
    else:
        user_is_verified = 'Вериф'
        call_is_verified = 'unverify'

    keyboard = [
        [InlineKeyboardButton(text='💵 Изм. баланса', callback_data='mamont|change_balance')],
        [InlineKeyboardButton(text='📥 Мин. депозит', callback_data='mamont|min_deposit'),
         InlineKeyboardButton(text='📤 Мин. вывод', callback_data='mamont|min_withdraw')],
        [InlineKeyboardButton(text=f'🔺 {user_is_verified}', callback_data=f'mamont|{call_is_verified}'),
         InlineKeyboardButton(text='🔰 Вывод', callback_data='mamont|withdraw'),
         InlineKeyboardButton(text='🔰 Покупка', callback_data='mamont|buying')],
        [InlineKeyboardButton(text='🔒 Заблокировать', callback_data='mamont|block')],
        [InlineKeyboardButton(text='🗑 Удалить лохматого', callback_data='mamont|delete')]
    ]

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    return keyboard_markup