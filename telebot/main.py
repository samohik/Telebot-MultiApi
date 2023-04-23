import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from pyowm.commons.exceptions import NotFoundError

from config import TELEGRAM_TOKEN
from telebot.func.exchange import Currency
from telebot.func.random_picture import get_picture
from telebot.func.weather import get_temperature_in_city


API_TOKEN = TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot, MemoryStorage and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def setup_bot_commands(dp):
    bot_commands = [
        types.BotCommand(command="/help", description="""
        /start
        /cute_animals
        /exchange
        /weather
        """),
        types.BotCommand(command="/cancel", description="Stop process"),
        types.BotCommand(command="/cute_animals", description="Send cute picture of the cats"),
        types.BotCommand(command="/exchange", description="Send exchange"),
        types.BotCommand(command="/weather", description="Send weather"),
    ]
    await bot.set_my_commands(bot_commands)


@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text="/help"),
        types.KeyboardButton(text="/cute_animals"),
        types.KeyboardButton(text="/exchange"),
        types.KeyboardButton(text="/weather"),
    ]
    keyboard.add(*buttons)

    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.", reply_markup=keyboard)


@dp.message_handler(commands=['cute_animals'])
async def get_animals(message: types.Message):
    logging.info('Enter in get_animals')
    try:
        result = get_picture()
        await message.reply_photo(result)
    except Exception as e:
        logging.exception(e)
        await message.answer('Somthing goes wrong try again')


class ExchangeForm(StatesGroup):
    data = State()  # Will be represented in storage as 'Form:name'


@dp.message_handler(commands=['exchange'])
async def get_exchange(message: types.Message):
    logging.info('Enter in get_exchange')
    await message.reply('Enter data like: 34 usd EUR')
    await ExchangeForm.data.set()


@dp.message_handler(state=ExchangeForm.data)
async def process_exchange(message: types.Message, state: FSMContext):
    """
    Get exchange from Exchange Rates.
    """
    logging.info('Enter in process_exchange')
    try:
        currency = Currency.convert_currency(message.text)
        result = currency.main()
        text = f"""
            {
                result["exchange"],
                result["from_currency"],
                result["to_currency"],
            }
        """
        await message.reply(text=text)
        await state.finish()

    except Exception as e:
        logging.exception(e)
        result = 'Try again.The data was incorrect'
        await message.reply(text=result)


class WeatherForm(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'


@dp.message_handler(commands=['weather'])
async def get_weather(message: types.Message):
    logging.info('Enter in get_weather')
    await message.reply("Enter name of the city")
    await WeatherForm.name.set()


@dp.message_handler(state=WeatherForm.name)
async def process_weather(message: types.Message, state: FSMContext):
    """
    Get weather from OpenWeatherMapApi and return temperature and status weather.
    """
    logging.info('Enter in process_weather')
    try:
        result = get_temperature_in_city(message.text)
        await message.reply(text=result)
        await state.finish()

    except NotFoundError as e:
        logging.exception(e)
        result = 'Try again.The name was incorrect'
        await message.reply(text=result)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)
