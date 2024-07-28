import aiohttp
from datetime import datetime
from nft_bot.databases.enums import CurrencyEnum
import logging

logger = logging.getLogger(__name__)


class CurrencyExchange:
    TIME_BETWEEN_UPDATE_COURSE = 1  # in hours

    def __init__(self):
        self.exchange_rates: dict[CurrencyEnum, float] = {}

    async def async_init(self):
        self.session = aiohttp.ClientSession()
        print('init self.session launched successfully!')

    async def reload_currencies_rates(self):
        url = f'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api\
@latest/v1/currencies/usd.min.json'
        async with self.session.get(url) as response:
            if response.status != 200:
                logger.info(f'Error: {response.status}, {await response.text()}')
                return
            data = (await response.json())['usd']
            print(data)
            self.exchange_rates[CurrencyEnum.usd] = 1.0
            self.exchange_rates[CurrencyEnum.rub] = data['rub']
            self.exchange_rates[CurrencyEnum.uah] = data['uah']
            self.exchange_rates[CurrencyEnum.eur] = data['eur']
            self.exchange_rates[CurrencyEnum.pln] = data['pln']
            self.exchange_rates[CurrencyEnum.byn] = data['byn']
            logger.info(f"Exchange rates updated: {self.exchange_rates}")
        self.last_reload_time = datetime.now()

    async def get_exchange_rate(self, to_currency: CurrencyEnum, amount: int) -> float:
        '''Return amount in to_currency from USD'''
        if to_currency == CurrencyEnum.usd:
            return amount

        if not self.exchange_rates or (
                datetime.now().hour - self.last_reload_time.hour
                >= self.TIME_BETWEEN_UPDATE_COURSE):
            await self.reload_currencies_rates()
        return self.exchange_rates[to_currency] * amount

    async def close(self):
        await self.session.close()


currency_exchange = CurrencyExchange()