from helper.helper import login_get_token, purge_database
import settings
import requests
import pytest
import json

token = login_get_token("admin", settings.ADMIN_PASSWORD)

# Delete Database before/after all tests


@pytest.fixture(autouse=True)
def run_around_tests():
    purge_database("admin", settings.ADMIN_PASSWORD)
    yield
    purge_database("admin", settings.ADMIN_PASSWORD)


example_device = {
    "title": "Laptop XY",
    "device_type": "laptop",
    "description": "High-quality laptop for professional use",
    "accessories": "power cable, ink cartridges",
    "serial_number": "ABD123456789",
    "rz_username_buyer": "john.doe",
    "rz_username_owner": "jane.doe",
    "room_code": "H 3",
    "cost_centre": 12345678,
    "seller": "Laptop AG",
    "timestamp_warranty_end": 1675840000,
    "timestamp_purchase": 1675860000,
    "price": "1300.00 €"
}


@pytest.fixture
def new_device_id():
    url = settings.BASE_URL + "/api/devices"

    header = {
        "accept": "application/json",
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=header, json=example_device)
    return response.json()["device_id"]


device_update_data = zip([
    {"title": "Laptop ABC"},  # change title
    # change title and description
    {"title": "Laptop ABC", "description": "Toller Laptop für alle"},
    # change device_type to invalid value "device"
    {"device_type": "device"},
    # update attribute that is not valid/part of the database model
    {"device_color": "black"},
    # changing the device_id should not be possible
    {"device_id": "abc"},
], [200, 200, 404, 422, 422])


@pytest.mark.parametrize("update_data, expected_response", device_update_data)
def test_update_device(new_device_id, update_data, expected_response):
    url = settings.BASE_URL + "/api/devices/"+new_device_id
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }

    response = requests.put(url, headers=headers, json=update_data)
    assert response.status_code == expected_response


# To test the other update routes, we need to load some dummy data
with open(settings.DUMMY_DATA_PATH, "r") as file:
    import_data = json.load(file)


owner_transaction_example_id = [device["owner_transaction_id"]
                                for device in import_data["owner_transactions"]][0]
location_transaction_example_id = [device["location_transaction_id"]
                                   for device in import_data["location_transactions"]][0]
purchasing_information_example_id = [device["purchasing_information_id"]
                                     for device in import_data["purchasing_information"]][0]


@pytest.fixture
def import_dummy_data():
    url = settings.BASE_URL + "/api/import"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }

    with open(settings.DUMMY_DATA_PATH, "r") as file:
        import_data = json.load(file)

    requests.post(url, headers=headers, json=import_data)


owner_transaction_update_data = zip([
    # change rz_username
    {"rz_username": "user123"},
    # update attribute that is not valid/part of the database model of owner_transaction
    {"owner_address": "Annahofstraße 1z 93049 Prüfening"},
    # changing the device_id should not be possible
    {"device_id": "a188957e-0184-4653-b950-7b98b86f8472"},
], [200, 422])


@pytest.mark.usefixtures("import_dummy_data")
@pytest.mark.parametrize("update_data, expected_response", owner_transaction_update_data)
def test_update_owner_transactions(update_data, expected_response):
    url = settings.BASE_URL + "/api/owner_transactions/" + owner_transaction_example_id

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }

    response = requests.put(url, headers=headers, json=update_data)
    assert response.status_code == expected_response


location_transaction_update_data = zip([
    # change room_code
    {"room_code": "H 4"},
    # update attribute that is not valid/part of the database model of location_transaction
    {"location_temperature": "22°"},
    # changing the device_id should not be possible
    {"device_id": "a188957e-0184-4653-b950-7b98b86f8472"},
], [200, 422, 422])


@pytest.mark.usefixtures("import_dummy_data")
@pytest.mark.parametrize("update_data, expected_response", location_transaction_update_data)
def test_update_location_transactions(update_data, expected_response):
    url = settings.BASE_URL + "/api/location_transactions/" + \
        location_transaction_example_id

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }

    response = requests.put(url, headers=headers, json=update_data)
    assert response.status_code == expected_response


purchasing_information_update_data = zip([
    # change price
    {"price": "236,39 €"},
    # change cost_centre value to valid value
    {"cost_centre": 12345678},
    # change cost_centre value to invalid value
    {"cost_centre": 123456789},
    # try to change non-existing key
    {"payer": "Max Mustermann"},
    # changing the device_id should not be possible
    {"device_id": "a188957e-0184-4653-b950-7b98b86f8472"},
], [200, 200, 404, 422, 422])


@pytest.mark.usefixtures("import_dummy_data")
@pytest.mark.parametrize("update_data, expected_response", purchasing_information_update_data)
def test_update_purchasing_information(update_data, expected_response):
    url = settings.BASE_URL + "/api/purchasing_information/" + \
        purchasing_information_example_id

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }

    response = requests.put(url, headers=headers, json=update_data)
    assert response.status_code == expected_response
