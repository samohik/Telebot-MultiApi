from pyowm import OWM
from telebot.config import WEATHER_TOKEN


def get_temperature_in_city(city: str):
    # initialize the OWM object with your API key
    owm = OWM(WEATHER_TOKEN)

    # get the weather for a city
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(city)
    weather = observation.weather

    # print the temperature in Celsius and status
    city = observation.location.name
    temperature = weather.temperature('celsius')['temp']
    status = weather.detailed_status
    result = "Temperature in {}: {} celsius\nWeather status: {}".format(city, temperature, status)
    return result


if __name__ == '__main__':
    print(get_temperature_in_city('New York'))
