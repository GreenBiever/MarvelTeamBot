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
    data = ['BRONZE', '2', '0', str(user.balance), '25000']
    image = image_generator.generate_image(data)
    image_path = FSInputFile(image)
    await message.answer_photo(photo=image_path, 
                               caption='<b>🔮 Профиль воркера</b>', parse_mode='HTML')
