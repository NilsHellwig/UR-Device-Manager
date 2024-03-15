from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import models, schemas, settings
from ..helper import *
import imghdr
import base64
import uuid
import os


def update_device(db: Session, device_id: str, device: schemas.DeviceUpdate, current_user: models.User):
    device_to_update = db.query(models.Device).filter(
        models.Device.device_id == device_id).first()

    device_to_update_dict = device.dict()
    uploaded_device_img = device_to_update_dict["uploaded_device_image"]

    image_id = ""
    # check if file uploaded by user
    if uploaded_device_img != None:
        if current_user.__dict__["has_admin_privileges"] == False:
            raise HTTPException(
                status_code=404, detail="Bilder von Geräten können nur mit Administrator-Rechten geändert werden.")

        # Source b64decode: https://docs.python.org/3/library/base64.html / imghdr: https://docs.python.org/3/library/imghdr.html
        header, encoded_image = uploaded_device_img.split(',', 1)
        image_id = str(uuid.uuid4())
        image_format = imghdr.what(None, base64.b64decode(encoded_image))

        if image_format != "jpeg" and image_format != "png":
            raise HTTPException(
                status_code=404, detail="Das Dateiformat wird für das Bild nicht unterstützt.")

    if uploaded_device_img != None:
        # upload new image
        image_url = settings.URL_STATIC_FILES + image_id + ".jpeg"

        image_binary = base64.b64decode(encoded_image)
        img_dir = "./public_images/"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        with open(img_dir + image_id + ".jpeg", 'wb') as file:
           file.write(image_binary)
        
        # remove existing image if it is a local image
        path_existing_image = device_to_update.__dict__["image_url"]
        if path_existing_image.startswith(settings.URL_STATIC_FILES):
            os.remove(img_dir + path_existing_image[len(settings.URL_STATIC_FILES):])



    for attr in device.__dict__:
        if getattr(device, attr) != None:
            if attr != "uploaded_device_image":
                setattr(device_to_update, attr, getattr(device, attr))
            else:
                setattr(device_to_update, "image_url", image_url)
    db.commit()
    return device_to_update


def update_owner_transaction(db: Session, owner_transaction_id: str, owner_transaction: schemas.OwnerTransactionUpdate):
    owner_transaction_to_update = db.query(models.OwnerTransaction).filter(
        models.OwnerTransaction.owner_transaction_id == owner_transaction_id).first()
    for attr in owner_transaction.__dict__:
        if getattr(owner_transaction, attr) != None:
            setattr(owner_transaction_to_update, attr,
                    getattr(owner_transaction, attr))
    db.commit()
    return owner_transaction_to_update


def update_location_transaction(db: Session, location_transaction_id: str, location_transaction: schemas.LocationTransactionUpdate):
    location_transaction_to_update = db.query(models.LocationTransaction).filter(
        models.LocationTransaction.location_transaction_id == location_transaction_id).first()
    for attr in location_transaction.__dict__:
        if getattr(location_transaction, attr) != None:
            setattr(location_transaction_to_update, attr,
                    getattr(location_transaction, attr))
    db.commit()
    return location_transaction_to_update


def update_purchasing_information(db: Session, purchasing_information_id: str, purchasing_information: schemas.PurchasingInformationUpdate):
    purchasing_information_to_update = db.query(models.PurchasingInformation).filter(
        models.PurchasingInformation.purchasing_information_id == purchasing_information_id).first()
    for attr in purchasing_information.__dict__:
        if getattr(purchasing_information, attr) != None:
            setattr(purchasing_information_to_update, attr,
                    getattr(purchasing_information, attr))
    db.commit()
    return purchasing_information_to_update
