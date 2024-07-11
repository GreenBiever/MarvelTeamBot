import json
import random
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, FSInputFile
from nft_bot.keyboards import kb
from nft_bot.databases import requests
from nft_bot.databases.enums import CurrencyEnum
from nft_bot.states import deposit_state, withdraw_state, admin_items_state
from nft_bot import config
from nft_bot.utils.get_exchange_rate import currency_exchange
from nft_bot.databases.models import User, Product


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


@router.message(F.text == '🎆 NFT')
async def admin_panel(message: types.Message):
    user = await requests.get_user_info(message.from_user.id)
    if user:
        status = await requests.get_user_status(message.from_user.id)
        lang = await requests.get_user_language(message.from_user.id)
        if status == "blocked":
            await message.answer(get_translation(lang, 'blocked'))
        else:
            collections_number = await requests.get_category_count()
            nft_text = get_translation(
                lang,
                'catalog_message',
                collections_number=collections_number
            )
            keyboard = await kb.create_collections_keyboard()
            photo = FSInputFile(config.PHOTO_PATH)
            await bot.send_photo(message.from_user.id, caption=nft_text, photo=photo, parse_mode="HTML", reply_markup=keyboard)
    else:
        await bot.send_message(message.from_user.id,
                               text=f'Выберите язык:\nSelect a language:',
                               parse_mode="HTML", reply_markup=kb.language)


@router.callback_query(lambda c: c.data.startswith('collection_'))
async def choose_collection(call: types.CallbackQuery):
    collection_id = call.data.split('_')[1]
    categories_with_count = await requests.get_categories_with_item_count_by_id(collection_id)

    if categories_with_count:
        category = categories_with_count[0]  # Поскольку мы ожидаем только одну категорию, берем первый элемент списка
        lang = await requests.get_user_language(call.from_user.id)
        nft_text = get_translation(
            lang,
            'collection_message',
            collection_name=category.name,
            number_of_tokens=category.item_count
        )
        keyboard = await kb.create_items_keyboard(collection_id)
        photo = FSInputFile(config.PHOTO_PATH)
        await bot.send_photo(call.from_user.id, caption=nft_text, photo=photo, parse_mode="HTML", reply_markup=keyboard)
    else:
        await call.answer("Category not found.", show_alert=True)


@router.callback_query(lambda c: c.data.startswith('token_'))
async def choose_item(call: types.CallbackQuery):
    item_id = call.data.split('_')[1]
    lang = await requests.get_user_language(call.from_user.id)
    item = await requests.get_item_info(item_id)

    if not item:
        await call.answer("Item not found")
        return

    user_currency = await requests.get_user_currency(call.from_user.id)
    item_price_usd = int(item.price)  # Assuming item.price is a string representing price in USD
    await currency_exchange.async_init()
    product_currency_price = await currency_exchange.get_exchange_rate(user_currency, item_price_usd)

    item_id, item_name, item_description, item_price, item_author, item_photo, category_name = item

    token_text = get_translation(
        lang,
        'token_message',
        token_name=item_name,
        item_description=item_description,
        category_name=category_name,
        item_author=item_author,
        item_price=item.price,
        item_currency_price=product_currency_price,
        user_currency=user_currency.value
    )
    keyboard = await kb.create_buy_keyboard(lang,  item_id)
    await bot.send_photo(call.from_user.id, caption=token_text, photo=item_photo, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith('buy_'))
async def buy_item(call: types.CallbackQuery):
    item_id = call.data.split('_')[1]
    lang = await requests.get_user_language(call.from_user.id)
    item = await requests.get_item_info(item_id)

    if not item:
        await call.answer("Item not found")
        return

    item_id, item_name, item_description, item_price, item_author, item_photo, category_name = item
    user_info = await requests.get_user_info(call.from_user.id)
    user_data, user_id, user_name, balance, currency, status, verification = user_info
    user_balance = balance
    if user_balance < int(item_price):
        token_text = get_translation(
            lang,
            'buy_no_balance',
            token_name=item_name,
            item_description=item_description,
            category_name=category_name,
            item_author=item_author,
            item_price=item.price
        )
    else:
        token_text = get_translation(
            lang,
            'buy_success',
            token_name=item_name,
            item_description=item_description,
            category_name=category_name,
            item_author=item_author,
            item_price=item.price
        )
    keyboard = await kb.create_buy_keyboard(lang, item_id)
    await call.answer(text=token_text, show_alert=False)


@router.callback_query(lambda c: c.data.startswith('add_to_favourites'))
async def add_to_favourites(call: types.CallbackQuery):
    item_id = call.data.split('_')[1]
    await requests.add_to_favourites(call.from_user.id, item_id)
    await call.answer("Item added to favourites")


@router.callback_query(lambda c: c.data.startswith('back_to_catalog'))
async def back_to_catalog(call: types.CallbackQuery):
    user = await requests.get_user_info(call.from_user.id)
    if user:
        status = await requests.get_user_status(call.from_user.id)
        lang = await requests.get_user_language(call.from_user.id)
        if status == "blocked":
            await call.answer(get_translation(lang, 'blocked'))
        else:
            collections_number = await requests.get_category_count()
            nft_text = get_translation(
                lang,
                'catalog_message',
                collections_number=collections_number
            )
            keyboard = await kb.create_collections_keyboard()
            photo = FSInputFile(config.PHOTO_PATH)
            await bot.send_photo(call.from_user.id, caption=nft_text, photo=photo, parse_mode="HTML",
                                 reply_markup=keyboard)
    else:
        await bot.send_message(call.from_user.id,
                               text=f'Выберите язык:\nSelect a language:',
                               parse_mode="HTML", reply_markup=kb.language)

