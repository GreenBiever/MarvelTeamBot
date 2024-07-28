from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile
from middlewares import IsVerifiedMiddleware, AuthorizeMiddleware
from services.images import image_generator
from database.models import User

router = Router()
router.message.middleware(AuthorizeMiddleware())
router.message.middleware(IsVerifiedMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())
router.callback_query.middleware(IsVerifiedMiddleware())


@router.message(F.text == '💎 Профиль')
async def profile(message: Message, user: User):
    try:
        data = ['BRONZE', '2', '0', str(user.balance), '25000']
        image = image_generator.generate_image(data)
        image_path = FSInputFile(image)
        text_caption = ('<b>🔮 Профиль воркера</b>\n\n'
                        f'Telegram ID: {user.tg_id}\n')
        await message.answer_photo(photo=image_path,
                                   caption='<b>🔮 Профиль воркера</b>', parse_mode='HTML')
    except Exception as e:
        await message.answer(text=f'Error: {e}')


@router.message(F.text == '💼 Трейд бот')
async def trade_bot(message: Message, user: User):
    referal_code = '0'
    phone_number = '0'  # TODO: create adding bank details and referral link
    card = '0'
    text = ('💼 <b>Трейд бот</b>\n'
            f'┖ Ваш код: {referal_code}\n\n'
            f'<b>Реквизиты</b>'
            f'┠ Телефон: {phone_number}\n'
            f'┖ Карта: {card}\n\n'
            f'<b>Ваша реферальная ссылка</b>\n'
            f'<a href=''>Нажми и скопируй</a>')
    await message.answer(text, parse_mode='HTML')

@router.message(F.text == '🎆 NFT бот')
async def nft_bot(message: Message, user: User):
    referal_code = '0'
    phone_number = '0'  # TODO: create adding bank details and referral link
    card = '0'
    text = ('🎆 <b>NFT бот</b>\n'
            f'┖ Ваш код: {referal_code}\n\n'
            f'<b>Реквизиты</b>'
            f'┠ Телефон: {phone_number}\n'
            f'┖ Карта: {card}\n\n'
            f'<b>Ваша реферальная ссылка</b>\n'
            f'<a href=''>Нажми и скопируй</a>')
    await message.answer(text, parse_mode='HTML')


@router.message(F.text == '🗽 О проекте')
async def about_project(message: Message, user: User):
    text = ('<b>🗽О проекте</b>\n\n')
    await message.answer(text, parse_mode='HTML')

