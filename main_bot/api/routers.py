from fastapi import APIRouter
from .schemas import Referal


router = APIRouter()


@router.post("/referals/")
async def new_referal(referal: Referal):
    '''Add new referal.
    Must be called from other bots when referal is created in nft_bot.'''
    # TODO: Add referal to database;
    # TODO: give bonus for referal for owner
