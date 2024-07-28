from aiogram import BaseMiddleware
from aiogram.types import Message
import logging
from database.models import User
from database.connect import async_session
from database.crud import register_referal
from sqlalchemy import select, update
from datetime import datetime
from utils.main_bot_api_client import LogRequest, main_bot_api_client, ReferalModel
import asyncio


class AuthorizeMiddleware(BaseMiddleware):
    '''Inject AsyncSession and User objects'''
    async def __call__(self, handler, event: Message, data) -> bool:
        async with async_session() as session:
            uid = event.from_user.id if hasattr(event, 'from_user') else event.message.from_user.id
            query = select(User).where(User.tg_id == uid)
            user: User | None = (await session.execute(query)).scalar()
            if not user:
                user = User(tg_id=str(event.from_user.id),
                            fname=event.from_user.first_name,
                            lname=event.from_user.last_name,
                            username=event.from_user.username
                            )
                if 'command' in data and (command := data['command']).args:
                     referer_tg_id = command.args
                     ref_model = ReferalModel(
                             referal_tg_id=user.tg_id,
                             referal_link_id=command.args,
                             fname=user.fname,
                             lname=user.lname,
                             username=user.username
                         )
                     asyncio.create_task(main_bot_api_client.send_referal(ref_model))
                     if (referer := (await session.scalar(
                        select(User).where(User.tg_id == referer_tg_id)
                     ))) and referer is not user: # referer exsist
                         await register_referal(session, referer, user)
                logger = logging.getLogger()
                logger.info(f'New user')
                session.add(user)
            query = update(User).where(User.tg_id==user.tg_id).values(last_login=datetime.now())
            await session.execute(query)
            await session.commit()
            data['user'] = user
            data['session'] = session
            result = await handler(event, data)
            await session.commit()
        return result


class IsAdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, message: Message, data) -> bool:
        user = data['user']
        if not user.is_admin:
            await message.answer('Вы не являетесь администратором. Войдите в админ панель, написав команду /a')
        else:
            return await handler(message, data)
