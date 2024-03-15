from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import models, schemas, settings
import imghdr
import base64
import uuid
import time
import os


def import_database(db: Session, database: dict):
    tables = [
        models.Device,
        models.LocationTransaction,
        models.OwnerTransaction,
        models.PurchasingInformation
    ]
    for key, model in zip(
        ["devices", "location_transactions",
            "owner_transactions", "purchasing_information"],
        tables
    ):
        try:
            for item in database[key]:
                db.add(model(**item))
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(rz_username=user.rz_username, has_admin_privileges=False,
                          full_name=user.full_name, organisation_unit=user.organisation_unit, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_device(db: Session, new_device_data: schemas.Device):
    new_device_data_dict = new_device_data.dict()

    uploaded_device_img = new_device_data_dict["uploaded_device_image"]
    image_id = ""
    # check if file uploaded by user
    if uploaded_device_img != None:
        # Source b64decode: https://docs.python.org/3/library/base64.html / imghdr: https://docs.python.org/3/library/imghdr.html
        header, encoded_image = uploaded_device_img.split(',', 1)
        image_id = str(uuid.uuid4())
        image_format = imghdr.what(None, base64.b64decode(encoded_image))

        if image_format != "jpeg" and image_format != "png":
            raise HTTPException(status_code=404, detail="Das Dateiformat wird für das Bild nicht unterstützt.")


    if image_id != "":
        image_url = settings.URL_STATIC_FILES + image_id + ".jpeg"
    else:
        image_url=f'https://pro.mi.ur.de/ase22-devices/{new_device_data_dict["device_type"]}.jpg'

    # store new device
    db_device = models.Device(device_id=str(
        uuid.uuid4()), title=new_device_data_dict["title"],
        device_type=new_device_data_dict["device_type"],
        description=new_device_data_dict["description"],
        accessories=new_device_data_dict["accessories"],
        serial_number=new_device_data_dict["serial_number"],
        rz_username_buyer=new_device_data_dict["rz_username_buyer"],
        image_url=image_url)

    device_id = db_device.__dict__["device_id"]
    # store new owner transaction
    db_owner_transaction = models.OwnerTransaction(owner_transaction_id=str(
        uuid.uuid4()), rz_username=new_device_data_dict["rz_username_owner"], timestamp_owner_since=time.time(), device_id=device_id)

    # store location transaction
    db_location_transaction = models.LocationTransaction(
        location_transaction_id=str(uuid.uuid4()), device_id=device_id,  room_code=new_device_data_dict["room_code"], timestamp_located_since=time.time())

    # store purchasing information
    db_purchasing_information = models.PurchasingInformation(
        purchasing_information_id=str(uuid.uuid4()), device_id=device_id, price=new_device_data_dict["price"], timestamp_warranty_end=new_device_data_dict["timestamp_warranty_end"], timestamp_purchase=new_device_data_dict["timestamp_purchase"], cost_centre=new_device_data_dict["cost_centre"], seller=new_device_data_dict["seller"])

    db.add(db_location_transaction)
    db.add(db_device)
    db.add(db_owner_transaction)
    db.add(db_purchasing_information)

    # upload image if available
    if uploaded_device_img != None:
        image_binary = base64.b64decode(encoded_image)
        img_dir = "./public_images/"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        with open(img_dir + image_id + ".jpeg", 'wb') as file:
           file.write(image_binary)

    db.commit()
    db.refresh(db_device)

    return db_device


def create_owner_transaction(db: Session, owner_transaction: schemas.OwnerTransaction):
    db_owner_transaction = models.OwnerTransaction(owner_transaction_id=str(
        uuid.uuid4()), timestamp_owner_since=time.time(), **owner_transaction.dict())
    db.add(db_owner_transaction)
    db.commit()
    db.refresh(db_owner_transaction)
    return db_owner_transaction


def create_location_transaction(db: Session, location_transaction: schemas.LocationTransaction):
    db_location_transaction = models.LocationTransaction(location_transaction_id=str(
        uuid.uuid4()), timestamp_located_since=time.time(), **location_transaction.dict())
    db.add(db_location_transaction)
    db.commit()
    db.refresh(db_location_transaction)
    return db_location_transaction


def create_purchasing_information(db: Session, purchasing_information: schemas.PurchasingInformation):
    db_purchasing_information = models.PurchasingInformation(
        purchasing_information_id=str(uuid.uuid4()), **purchasing_information.dict())
    db.add(db_purchasing_information)
    db.commit()
    db.refresh(db_purchasing_information)
    return db_purchasing_information
