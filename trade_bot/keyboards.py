from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Торговая площадка', callback_data='trade'))
    kb.row(InlineKeyboardButton(text='Кошелёк', callback_data='wallet'))
    kb.row(InlineKeyboardButton(text='Сменить язык', callback_data='change_lang'),
           InlineKeyboardButton(text='Сменить валюту', callback_data='change_currency'))
    kb.row(InlineKeyboardButton(text="Тех.поддержка", callback_data='support'))
    return kb.as_markup()

def get_wallet_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Пополнить', callback_data='top_up'),
           InlineKeyboardButton(text='Вывести', callback_data='withdraw'))
    kb.row(InlineKeyboardButton(text='Промокод', callback_data='promocode'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data='back'))
    return kb.as_markup()

def get_top_up_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Карта", callback_data='card'),
           InlineKeyboardButton(text="Криптовалюта", callback_data='crypto'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data='back'))
    return kb.as_markup()

def get_select_crypto_currency_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='BTC', callback_data='crypto_currency_btc'))
    kb.row(InlineKeyboardButton(text='ETH', callback_data='crypto_currency_eth'))
    kb.row(InlineKeyboardButton(text='USDT[TRC-20]', callback_data='crypto_currency_usdt'))
    return kb.as_markup()

def get_support_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Проверить оплату', callback_data='check_payment'))
    kb.row(InlineKeyboardButton(text='Тех.поддержка', callback_data='support'))
    return kb.as_markup()

def get_back_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Назад', callback_data='back'))
    return kb.as_markup()