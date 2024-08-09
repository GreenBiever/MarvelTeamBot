from typing import List

from fastapi import APIRouter, Query, Request, Path, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.schemas import UserProfile, OrderView
from database.crud import get_user_by_tg_id, update_user_profile, add_order
from database.connect import get_session
from database.models import Order
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
templates = Jinja2Templates(directory="okx")


@router.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request, trade: str = Query(), id: str = Query()):
    return templates.TemplateResponse(
        request=request, name="/ru/index.html", context={"id": id}
    )


@router.post("/user/{user_tg_id}/orders/")
async def add_user_orders(order: OrderView, user_tg_id: int = Path(),
                          session: AsyncSession = Depends(get_session)):
    user = await get_user_by_tg_id(session, user_tg_id)
    await add_order(session, user=user, order=Order(**order.model_dump()))
    await session.commit()

@router.get("/user/{user_tg_id}/", response_model=UserProfile)
async def get_user_profile(user_tg_id: int = Path(),
                           session: AsyncSession = Depends(get_session)):
    user = await get_user_by_tg_id(session, user_tg_id)
    await session.refresh(user, ['orders'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/user/profiles/", status_code=204) # Deprecated
async def set_user_profile(profile: UserProfile,
                           session: AsyncSession = Depends(get_session)):
    await update_user_profile(session, profile.user_tg_id, profile.model_dump())
