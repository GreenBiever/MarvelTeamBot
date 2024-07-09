from pydantic import BaseModel


class UserProfile(BaseModel):
    tg_id: int
    balance: int
    min_deposit: int
    min_withdraw: int
    is_verified: bool
    purchase_enabled: bool
    output_enabled: bool
    is_blocked: bool

    class Config:
        from_attributes = True