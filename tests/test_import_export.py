from helper.helper import login_get_token, purge_database
import settings
import urllib.parse
import requests
import pytest
import json

# $ pytest tests --no-header -vv


token = login_get_token("admin", settings.ADMIN_PASSWORD)

# Delete Database before/after all tests: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html


@pytest.fixture(autouse=True)
def run_around_tests():
    purge_database("admin", settings.ADMIN_PASSWORD)
    yield
    purge_database("admin", settings.ADMIN_PASSWORD)


def test_purge():
    url = settings.BASE_URL + "/api/purge"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + token
    }
    response = requests.delete(url, headers=headers)
    assert response.status_code == 204


def test_import():
    url = settings.BASE_URL + "/api/import"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }

    with open(settings.DUMMY_DATA_PATH, "r") as file:
        import_data = json.load(file)

    response = requests.post(url, headers=headers, json=import_data)
    assert response.status_code == 201


def test_export():
    url = settings.BASE_URL + "/api/export"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + token
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
