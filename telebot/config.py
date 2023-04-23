import os
from dotenv import load_dotenv

load_dotenv()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_TOKEN = os.getenv("WEATHER_TOKEN")
EXCHANGE_TOKEN = os.getenv("EXCHANGE_TOKEN")
