import requests
from telebot.config import CAT_TOKEN


class NoImage(Exception):
    pass


def get_picture():
    """
    Get picture the return.
    :return: Bytes
    """
    url = "https://some-random-api.ml/img/cat"
    params = {"api_key": CAT_TOKEN}
    response = requests.get(url=url, params=params)
    if response.status_code == 200:
        data = response.json()
        image_url = data["link"]
        return image_url
    else:
        raise NoImage


if __name__ == "__main__":
    get_picture()
