import requests


def get_picture() -> bytes:
    """
    Get picture the return.
    :return: Bytes
    """
    response = requests.get('https://cataas.com/cat')
    image_data = response.content
    return image_data

