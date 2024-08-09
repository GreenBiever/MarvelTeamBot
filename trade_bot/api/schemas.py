from pydantic import BaseModel, field_validator
from datetime import datetime


class OrderView(BaseModel):
    cryptocurrency: str
    amount: int
    time: datetime
    bets_result_win: bool  # False - lose, True - win
    profit: int
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    tg_id: int
    balance: int
    min_deposit: int
    min_withdraw: int
    is_verified: bool
    purchase_enabled: bool
    output_enabled: bool
    bidding_blocked: bool
    is_blocked: bool
    bets_result_win: bool | None # False - alway must lose, True - win, None - random
    
    orders: list[OrderView]

    @field_validator('orders', mode='before')
    @classmethod
    def convert_int_serial(cls, val):
        return list(map(lambda v: OrderView.model_validate(v), val))

    class Config:
        from_attributes = True


