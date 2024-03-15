from helper.helper import login_get_token, purge_database
import settings
import requests
import pytest
import json

token = login_get_token("user", settings.TEST_STANDARD_USER_PASSWORD)

# Delete Database before/after all tests


@pytest.fixture(autouse=True)
def run_around_tests():
    purge_database("admin", settings.ADMIN_PASSWORD)
    yield
    purge_database("admin", settings.ADMIN_PASSWORD)


@pytest.fixture
def import_dummy_data():
    url = settings.BASE_URL + "/api/import"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + login_get_token("admin", settings.ADMIN_PASSWORD)
    }

    with open(settings.DUMMY_DATA_PATH, "r") as file:
        import_data = json.load(file)

    requests.post(url, headers=headers, json=import_data)


# To test the other update routes, we need to load some dummy data
with open(settings.DUMMY_DATA_PATH, "r") as file:
    import_data = json.load(file)


@pytest.mark.usefixtures("import_dummy_data")
@pytest.mark.parametrize("device_id", [device["device_id"] for device in import_data["devices"]])
def test_get_device(device_id):
    url = settings.BASE_URL + "/api/devices/" + device_id
    headers = {"accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.usefixtures("import_dummy_data")
def test_get_all_device():
    url = settings.BASE_URL + "/api/devices/"
    headers = {"accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.usefixtures("import_dummy_data")
@pytest.mark.parametrize("owner_transaction_id", [owner_transaction["owner_transaction_id"] for owner_transaction in import_data["owner_transactions"]])
def test_get_owner_transaction(owner_transaction_id):
    url = settings.BASE_URL + "/api/owner_transactions/" + owner_transaction_id
    headers = {"accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.usefixtures("import_dummy_data")
def test_get_all_owner_transaction():
    url = settings.BASE_URL + "/api/owner_transactions/"
    headers = {"accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.usefixtures("import_dummy_data")
@pytest.mark.parametrize("location_transaction_id", [location_transaction["location_transaction_id"] for location_transaction in import_data["location_transactions"]])
def test_get_location_transaction(location_transaction_id):
    url = settings.BASE_URL + "/api/location_transactions/" + location_transaction_id
    headers = {"accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.usefixtures("import_dummy_data")
def test_get_all_location_transaction():
    url = settings.BASE_URL + "/api/location_transactions/"
    headers = {"accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.usefixtures("import_dummy_data")
@pytest.mark.parametrize("purchasing_information_id", [purchasing_information["purchasing_information_id"] for purchasing_information in import_data["purchasing_information"]])
def test_get_purchasing_information(purchasing_information_id):
    url = settings.BASE_URL + "/api/purchasing_information/" + purchasing_information_id
    headers = {"accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.usefixtures("import_dummy_data")
def test_get_all_purchasing_information():
    url = settings.BASE_URL + "/api/purchasing_information/"
    headers = {"accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
