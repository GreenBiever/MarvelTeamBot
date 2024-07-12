from fastapi import APIRouter, Depends
from .schemas import Referal
from database.methods import add_referal
from database.connect import get_session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.post("/referals/")
async def new_referal(referal: Referal, session: AsyncSession = Depends(get_session)):
    '''Add new referal.
    Must be called from other bots when referal is created in nft_bot.'''
    await add_referal(session, referal)
    # TODO: give bonus for referal for owner
