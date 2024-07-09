from pydantic import BaseModel


class Referal(BaseModel):
    referal_tg_id: str
    referal_link_id: str