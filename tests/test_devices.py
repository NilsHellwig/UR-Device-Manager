from helper.helper import login_get_token, purge_database
import settings
import requests
import pytest


"""
  Dummy Data created with ChatGPT
  PROMPT:
  schreibe mir dummy daten mit anderen daten in diesem format:

{
    # invalid cost_centre
    "title": "Laptop XY",
    "device_type": "table",
    "description": "High-quality laptop for professional use",
    "accessories": "power cable, ink cartridges",
    "serial_number": "ABD123456789",
    "rz_username_buyer": "john.doe",
    "rz_username_owner": "jane.doe",
    "room_code": "H 3",
    "cost_centre": 1234567890,
    "seller": "Laptop AG",
    "timestamp_warranty_end": 1675840000,
    "timestamp_purchase": 1675860000,
    "price": "1300.00 €"
}
"""

dummy_valid_data_devices = [{
    "title": "Computer XY",
    "device_type": "computer",
    "description": "High-quality computer for professional use",
    "accessories": "power cable",
    "serial_number": "ABC123456789",
    "rz_username_buyer": "john.doe",
    "rz_username_owner": "jane.doe",
    "room_code": "H 2",
    "cost_centre": 12345678,
    "seller": "Computer AG",
    "timestamp_warranty_end": 1675860264,
    "timestamp_purchase": 1675860000,
    "price": "300.00 €"
}, {
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
}]

dummy_invalid_devices_data = [{
    # missing title
    "title": "",
    "device_type": "computer",
    "description": "High-quality computer for professional use",
    "accessories": "power cable",
    "serial_number": "ABC123456789",
    "rz_username_buyer": "john.doe",
    "rz_username_owner": "jane.doe",
    "room_code": "H 2",
    "cost_centre": 12345678,
    "seller": "Computer AG",
    "timestamp_warranty_end": 1675860264,
    "timestamp_purchase": 1675860000,
    "price": "300.00 €"
}, {
    # invalid device_type
    "title": "Laptop XY",
    "device_type": "device", # type device does not exist
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
}, {
    # invalid cost_centre
    "title": "Laptop XY",
    "device_type": "laptop",
    "description": "High-quality laptop for professional use",
    "accessories": "power cable, ink cartridges",
    "serial_number": "ABD123456789",
    "rz_username_buyer": "john.doe",
    "rz_username_owner": "jane.doe",
    "room_code": "H 3",
    "cost_centre": 122,
    "seller": "Laptop AG",
    "timestamp_warranty_end": 1675840000,
    "timestamp_purchase": 1675860000,
    "price": "1300.00 €"
}, {
    # invalid room number
    "title": "Laptop 123",
    "device_type": "laptop",
    "description": "Top-of-the-line laptop with large display and long battery life",
    "accessories": "charging cable",
    "serial_number": "BAC987654321",
    "rz_username_buyer": "jane.doe",
    "rz_username_owner": "john.doe",
    "room_code": "E 643",
    "cost_centre": 12345678,
    "seller": "Phone Co.",
    "timestamp_warranty_end": 1675840000,
    "timestamp_purchase": 1675940000,
    "price": "800.00 €"
}, ]

dummy_invalid_devices_response = ["Gerätename muss mindestens ein Zeichen lang sein.", "device ist keine valider Wert für den Gerätetyp.",
                                  "Die Kostenstelle muss eine 8-stellige Zahl sein", "Dies ist keine valide Raumnummer."]

token = login_get_token("admin", settings.ADMIN_PASSWORD)

# Delete Database before/after all tests


@pytest.fixture(autouse=True)
def run_around_tests():
    purge_database("admin", settings.ADMIN_PASSWORD)
    yield
    purge_database("admin", settings.ADMIN_PASSWORD)


def delete_device(device_id):
    url = settings.BASE_URL + "/api/devices/" + device_id
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + token
    }
    delete_response = requests.delete(url, headers=headers)

    assert delete_response.status_code == 204

# if a device got deleted, this function is intended to make sure that related
# location_transactions are deleted


def check_if_location_transactions_deleted(device_id):
    url = settings.BASE_URL + "/api/location_transactions"
    response = requests.get(
        url, headers={"accept": "application/json", "Authorization": "Bearer " + token})
    assert response.status_code == 200
    location_transactions_for_device_id = [
        transaction for transaction in response.json() if transaction["device_id"] == device_id]
    assert len(location_transactions_for_device_id) == 0


@pytest.mark.parametrize("device", dummy_valid_data_devices)
def test_add_delete_get_device(device):
    url = settings.BASE_URL + "/api/devices"

    header = {
        "accept": "application/json",
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=header, json=device)
    delete_device(response.json()["device_id"])
    check_if_location_transactions_deleted(response.json()["device_id"])

    assert response.status_code == 201
    assert response.headers["content-type"] == "application/json"


@pytest.mark.parametrize("device, expected_response", zip(dummy_invalid_devices_data, dummy_invalid_devices_response))
def test_add_invalid_device_schema(device, expected_response):
    url = settings.BASE_URL + "/api/devices"

    header = {
        "accept": "application/json",
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=header, json=device)

    assert response.json()["detail"] == expected_response
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"


def test_get_all_devices():
    url = settings.BASE_URL + "/api/devices"
    response = requests.get(
        url, headers={"accept": "application/json", "Authorization": "Bearer " + token})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
