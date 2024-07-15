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