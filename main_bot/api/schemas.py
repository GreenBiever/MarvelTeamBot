from pydantic import BaseModel


class ReferalModel(BaseModel):
    referal_tg_id: str
    referal_link_id: str
    fname: str | None
    lname: str | None
    username: str | None