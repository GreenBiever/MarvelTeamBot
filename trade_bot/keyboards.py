from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import config


def get_main_kb(kb_lang_data: dict) -> InlineKeyboardMarkup:
    lang_data = kb_lang_data['buttons']['main_kb']
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=lang_data['trade'], callback_data='trade'))
    kb.row(InlineKeyboardButton(text=lang_data['wallet'], callback_data='wallet'))
    kb.row(InlineKeyboardButton(text=lang_data['change_lang'], callback_data='change_lang'),
           InlineKeyboardButton(text=lang_data['change_currency'], 
                                callback_data='change_currency'))
    kb.row(InlineKeyboardButton(text=lang_data['support'], callback_data='support'))
    return kb.as_markup()

def get_trade_kb(kb_lang_data: dict, user_tg_id: str) -> InlineKeyboardMarkup:
    lang_data = kb_lang_data['buttons']['trade_kb']
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='FAQ', callback_data='trade_faq'))
    kb.row(InlineKeyboardButton(text=lang_data['crypto'], 
           url=f"{config.WEBHOOK_URL}:{config.WEBHOOK_PORT}/?\
trade=BINANCE:BTCUSDT&id={user_tg_id}"))
    kb.row(InlineKeyboardButton(text=lang_data['back'], callback_data='back'))
    return kb.as_markup()

def get_wallet_kb(kb_lang_data: dict) -> InlineKeyboardMarkup:
    lang_data = kb_lang_data['buttons']['wallet_kb']
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=lang_data['top_up'], callback_data='top_up'))
    kb.row(InlineKeyboardButton(text=lang_data['withdraw'], callback_data='withdraw'))
    kb.row(InlineKeyboardButton(text=lang_data['promocode'], callback_data='promocode'))
    kb.row(InlineKeyboardButton(text=lang_data['back'], callback_data='back'))
    return kb.as_markup()

def get_top_up_kb(kb_lang_data: dict) -> InlineKeyboardMarkup:
    lang_data = kb_lang_data['buttons']['top_up_kb']
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=lang_data['card'], callback_data='card'))
    kb.row(InlineKeyboardButton(text=lang_data['crypto'], callback_data='crypto'))
    kb.row(InlineKeyboardButton(text=lang_data['back'], callback_data='back'))
    return kb.as_markup()

def get_select_crypto_currency_kb(kb_lang_data: dict = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='BTC', callback_data='crypto_currency_btc'))
    kb.row(InlineKeyboardButton(text='ETH', callback_data='crypto_currency_eth'))
    kb.row(InlineKeyboardButton(text='USDT[TRC-20]', callback_data='crypto_currency_usdt'))
    return kb.as_markup()

def get_support_kb(kb_lang_data: dict) -> InlineKeyboardMarkup:
    lang_data = kb_lang_data['buttons']['support_kb']

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=lang_data['check_payment'],
                                 callback_data='check_payment'))
    kb.row(InlineKeyboardButton(text=lang_data['support'], callback_data='support'))
    return kb.as_markup()

def get_back_kb(kb_lang_data: dict) -> InlineKeyboardMarkup:
    lang_data = kb_lang_data['buttons']['back_kb']
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=lang_data['back'], callback_data='back'))
    return kb.as_markup()


def get_select_lang_kb(kb_lang_data: dict = None) -> InlineKeyboardMarkup:
    kb_lang_data = kb_lang_data['buttons']['select_lang_kb']
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Русский', callback_data='set_lang_ru'),
           InlineKeyboardButton(text='English', callback_data='set_lang_en'))
    kb.row(InlineKeyboardButton(text='Польский', callback_data='set_lang_pl'),
           InlineKeyboardButton(text='Украинский', callback_data='set_lang_ua'))
    kb.row(InlineKeyboardButton(text=kb_lang_data['back'], callback_data='back'))
    return kb.as_markup()


def get_select_currency_kb(kb_lang_data: dict) -> InlineKeyboardMarkup:
    lang_data = kb_lang_data['buttons']['select_currency_kb']
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='USD', callback_data='set_currency_usd'),
           InlineKeyboardButton(text='EUR', callback_data='set_currency_eur'))
    kb.row(InlineKeyboardButton(text='RUB', callback_data='set_currency_rub'),
           InlineKeyboardButton(text='UAH', callback_data='set_currency_uah'))
    kb.row(InlineKeyboardButton(text=lang_data['back'], callback_data='back'))
    return kb.as_markup()


def get_support_page_kb(kb_lang_data: dict) -> InlineKeyboardMarkup:
    lang_data = kb_lang_data['buttons']['support_page_kb']
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=lang_data['support'], url='https://google.com/'))
    kb.row(InlineKeyboardButton(text=lang_data['back'], callback_data='back'))
    return kb.as_markup()