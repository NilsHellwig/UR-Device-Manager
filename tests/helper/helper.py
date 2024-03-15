import settings
import requests
import pytest


def login_get_token(username, password):
    url = settings.BASE_URL + "/api/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": username,
        "password": password,
    }
    response = requests.post(url, headers=headers, data=data)
    token = response.json()["access_token"]
    return token


def purge_database(username, password):
    url = settings.BASE_URL + "/api/purge"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + login_get_token(username, password)
    }
    response = requests.delete(url, headers=headers)
