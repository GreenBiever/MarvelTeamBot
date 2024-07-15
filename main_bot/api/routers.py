from fastapi import APIRouter, Depends
from .schemas import ReferalModel, LogRequest
from database.methods import (add_referal, get_user_by_their_referal, get_user_by_tg_id)
from database.connect import get_session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

from utils.bot_methods import bot, send_notification_of_referal


@router.post("/referals/")
async def new_referal(referal: ReferalModel, session: AsyncSession = Depends(get_session)):
    '''Add new referal.
    Must be called from other bots when referal is created in nft_bot.'''
    if not referal.referal_link_id.startswith('w'):
        return
    referal.referal_link_id = referal.referal_link_id[1:] # remove 'w'
    referer = await get_user_by_tg_id(session, referal.referal_link_id)
    if not referer:
        await send_notification_of_referal(referal.referal_tg_id)
    else:
        
        await add_referal(session, referal)
        await bot.send_message(referer.tg_id, 
                               f"По вашей ссылке зарегистрировался новый пользователь. \
Его ID: {referal.referal_tg_id}")


@router.post("/referals/logs/")
async def create_log(log_request: LogRequest, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_their_referal(session, log_request.user_tg_id)
    await bot.send_message(user.tg_id, f'Пользователь {log_request.user_tg_id} \
совершил дейтсвие:\n {log_request.log_text}')
