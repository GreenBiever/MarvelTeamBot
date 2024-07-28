from pydantic import BaseModel


class ReferalModel(BaseModel):
    referal_tg_id: str
    referal_link_id: str
    fname: str | None = None
    lname: str | None = None
    username: str | None = None


class LogRequest(BaseModel):
    user_tg_id: str
    log_text: str


class Promocode(BaseModel):
    creator_tg_id: int
    code: str
    amount: int
    number_of_activations: int = 1

    class Config:
        from_attributes = True

class PromocodeActivate(BaseModel):
    code: str
    tg_id: int

class PromocodeOut(BaseModel):
    available: bool
    promocode: Promocode | None = None
    

class PaymentProps(BaseModel):
    card: str

class TradeBotPaymentProps(PaymentProps):
    eth_wallet: str
    ...

class NftBotPaymentProps(PaymentProps):
    btc_wallet: str