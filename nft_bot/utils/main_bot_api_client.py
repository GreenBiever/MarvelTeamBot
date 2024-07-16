import aiohttp
from pydantic import BaseModel
from nft_bot import config


class LogRequest(BaseModel):
    user_tg_id: str
    log_text: str


class ReferalModel(BaseModel):
    referal_tg_id: str
    referal_link_id: str
    fname: str | None = None
    lname: str | None = None
    username: str | None = None


class MainBotApiClient:
    async def async_init(self, session: aiohttp.ClientSession = None):
        self.session = session or aiohttp.ClientSession()

    async def send_log_request(self, log_request: LogRequest):
        url = f"{config.WEBSITE_URL}/referals/log/"
        async with self.session.post(url, json=log_request.model_dump()) as response:
            if response.status != 200:
                raise Exception('Main bot api not found')

    async def send_referal(self, referal_model: ReferalModel):
        url = f"{config.WEBSITE_URL}/referals/"
        async with self.session.post(url, json=referal_model.model_dump()) as response:
            if response.status != 200:
                raise Exception('Main bot api not found')

    async def close(self):
        await self.session.close()


main_bot_api_client = MainBotApiClient()