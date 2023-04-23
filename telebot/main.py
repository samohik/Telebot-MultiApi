import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

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
        types.BotCommand(command="/cancel", description="Stop process"),
        types.BotCommand(command="/create_poll", description="Create poll"),
        types.BotCommand(
            command="/cute_animals",
            description="Send cute picture of the cats",
        ),
        types.BotCommand(command="/exchange", description="Send exchange"),
        types.BotCommand(command="/weather", description="Send weather"),
    ]
    await bot.set_my_commands(bot_commands)


@dp.message_handler(commands=["start"], state="*")
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text="/create_poll"),
        types.KeyboardButton(text="/cute_animals"),
        types.KeyboardButton(text="/exchange"),
        types.KeyboardButton(text="/weather"),
    ]
    keyboard.add(*buttons)

    await message.answer(
        "Hi!\nI'm EchoBot!\nPowered by aiogram.", reply_markup=keyboard
    )


@dp.message_handler(commands=["cute_animals"])
async def get_animals(message: types.Message):
    """
    Returns a photo of an animal randomly
    """
    logging.info("Enter in get_animals")
    try:
        result = get_picture()
        await message.reply(result)
    except Exception as e:
        logging.exception(e)
        await message.answer("Somthing goes wrong try again")


class ExchangeForm(StatesGroup):
    data = State()  # Will be represented in storage as 'Form:name'


@dp.message_handler(commands=["exchange"])
async def get_exchange(message: types.Message):
    """
    Takes a value from one currency to another.
    """
    logging.info("Enter in get_exchange")
    await message.answer("Enter data like: 100 USD EUR")
    await ExchangeForm.data.set()


@dp.message_handler(state=ExchangeForm.data)
async def process_date(message: types.Message, state: FSMContext):
    """
    Process data
    """
    logging.info("Enter in process_exchange")
    try:
        currency = Currency(message.text)
        result = currency.main()
        text = f'From {result["from_rate"]} in {result["to_rate"]}: {result["exchange"]}'
        await message.answer(text=text)
        await state.finish()

    except Exception as e:
        logging.exception(e)
        result = "Try again.The data was incorrect"
        await message.answer(text=result)


class WeatherForm(StatesGroup):
    name = State()


@dp.message_handler(commands=["weather"])
async def get_weather(message: types.Message):
    """
    Accepts city and returns temperature and status.
    """
    logging.info("Enter in get_weather")
    await message.answer("Enter name of the city")
    await WeatherForm.name.set()


@dp.message_handler(state=WeatherForm.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process name
    """
    logging.info("Enter in process_weather")
    try:
        result = get_temperature_in_city(message.text)
        await message.answer(text=result)
        await state.finish()

    except Exception as e:
        logging.exception(e)
        result = "Try again.The name was incorrect"
        await message.answer(text=result)


class PollForm(StatesGroup):
    question = State()
    answers = State()
    group_id = State()


@dp.message_handler(commands=["create_poll"])
async def get_poll(message: types.Message):
    """
    Creates a poll and sends it to the group
    """
    logging.info("Enter in get_poll")
    await message.answer("Enter a question")
    await PollForm.question.set()


@dp.message_handler(state=PollForm.question)
async def process_question(message: types.Message, state: FSMContext):
    """
    Process question
    """
    logging.info("Enter in process_question")
    async with state.proxy() as data:
        data["question"] = message.text
    await PollForm.next()
    await message.answer("Enter answers separated by two spaces")


@dp.message_handler(state=PollForm.answers)
async def process_answers(message: types.Message, state: FSMContext):
    """
    Process answers
    """
    logging.info("Enter in process_answers")
    async with state.proxy() as data:
        options = message.text.split("  ")
        if len(options) > 1:
            data["answers"] = options
            await PollForm.next()
            await message.answer("Create group id")
        else:
            await message.answer("Poll must have at least 2 option")


@dp.message_handler(state=PollForm.group_id)
async def process_group_id(message: types.Message, state: FSMContext):
    """
    Process group id and send poll
    """
    logging.info("Enter in process_group_id")
    async with state.proxy() as data:
        data["group_id"] = message.text
    try:
        # Description poll
        poll = types.Poll(
            question=data["question"],
            options=data["answers"],
            is_anonymous=False,
        )

        # Send poll
        await bot.send_poll(
            data["group_id"],
            question=poll.question,
            options=poll.options,
            is_anonymous=poll.is_anonymous,
            reply_markup=poll,
        )

        # Finish conversation
        await state.finish()
    except Exception as e:
        logging.exception(e)
        await message.answer("Invalid group id try again")


# You can use state '*' if you need to handle all states
@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply("Cancelled.", reply_markup=types.ReplyKeyboardRemove())


if __name__ == "__main__":
    executor.start_polling(
        dp, skip_updates=True, on_startup=setup_bot_commands
    )
