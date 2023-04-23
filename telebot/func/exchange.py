import re
from typing import Dict, Type

import requests

from telebot.config import EXCHANGE_TOKEN


class Currency:
    def __init__(self, data: str):
        self.data: str = data
        self.amount = None
        self.from_currency = None
        self.to_currency = None
        self.result: Dict = {}

    def main(self) -> Dict[str, float | str]:
        self.check_data()
        self.convert_currency()
        return self.result

    def check_data(self):
        pattern = r'(\d+.?\d+) (\w{3}) (\w{3})'
        match = re.search(pattern, self.data)
        self.amount, self.from_currency, self.to_currency = match.groups()

    def convert_currency(self):
        # Ваш API-ключ Open Exchange Rates API
        api_key = EXCHANGE_TOKEN
        url = f'https://openexchangerates.org/api/latest.json'
        params = {'app_id': {api_key}}

        # Получаем актуальный курс обмена валют
        response = requests.get(url, params=params).json()
        rates = response['rates']
        from_rate = rates[self.from_currency.upper()]
        to_rate = rates[self.to_currency.upper()]

        # Конвертируем валюты
        exchange = (float(self.amount) / from_rate) * to_rate
        self.result = {
            'exchange': round(exchange, 2),
            'from_rate': self.from_currency.upper(),
            'to_rate': self.to_currency.upper()
        }


if __name__ == '__main__':
    # user_input = '23.7 usd EUR'
    user_input = '1200 byn eur'
    x = Currency(user_input)
    print(x.main())


