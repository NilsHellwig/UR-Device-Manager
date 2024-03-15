import settings
import requests
import pytest
from helper.helper import login_get_token


def check_auth(token):
    url = settings.BASE_URL + "/api/check_auth"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + token
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'


@pytest.mark.parametrize("user", [
    {
        "username": "user",
        "password": settings.TEST_STANDARD_USER_PASSWORD,
    }
])
def test_correct_login(user):
    url = settings.BASE_URL + "/api/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, headers=headers, data=user)

    token = response.json()["access_token"]
    check_auth(token)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'


@pytest.mark.parametrize("username, password, expected_response", [
    ("user", "testabc", "Passwort"),
    ("user2", "test123", "RZ-Username"),
])
def test_incorrect_login(username, password, expected_response):
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

    assert response.status_code == 404
    assert response.json()["detail"] == expected_response
    assert response.headers['content-type'] == 'application/json'


@pytest.mark.parametrize("username, password, organisation_unit, full_name", [
    ("user_neu1", "123456789", "Rechenzentrum", "Martina Mustermann"),
    ("user_neu2", "123456789", "Rechenzentrum", "Max Mustermann"),
])
def test_register(username, password, organisation_unit, full_name):
    url = settings.BASE_URL + "/api/register"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + login_get_token("admin", settings.ADMIN_PASSWORD)
    }
    data = {
        "rz_username": username,
        "password": password,
        "full_name": full_name,
        "organisation_unit": organisation_unit
    }
    response = requests.post(url, headers=headers, json=data)

    assert response.status_code == 201
    assert response.headers['content-type'] == 'application/json'


@pytest.mark.parametrize("username, expected_response", [
    ("user_neu1", 204),
    ("user_neu2", 204),
])
def test_remove_user(username, expected_response):
    headers_delete_request = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + login_get_token("admin", settings.ADMIN_PASSWORD)
    }

    response = requests.delete(
 f'{settings.BASE_URL}/api/users/{username}', headers=headers_delete_request)

    assert response.status_code == expected_response
