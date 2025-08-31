import requests


def is_accessible(url) -> bool:
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False
