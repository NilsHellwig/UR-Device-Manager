from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer, select
from .. import models


def export_database(db):
    database_dict = {
        "devices": [x.__dict__ for x in db.query(models.Device).all()],
        "owner_transactions": [x.__dict__ for x in db.query(models.OwnerTransaction).all()],
        "location_transactions": [x.__dict__ for x in db.query(models.LocationTransaction).all()],
        "purchasing_information": [x.__dict__ for x in db.query(models.PurchasingInformation).all()]
    }

    return database_dict

# GET Single Requests


def get_user(db: Session, rz_username: str):
    return db.query(models.User).filter(models.User.rz_username == rz_username).first()


def get_device(db: Session, device_id: str, detailed_data: bool):
    device = db.query(models.Device).filter(
        models.Device.device_id == device_id).first()
    if detailed_data:
        owners = db.query(models.OwnerTransaction).filter(
            models.OwnerTransaction.device_id == device.__dict__["device_id"]).all()
        location = db.query(models.LocationTransaction).filter(
            models.LocationTransaction.device_id == device.__dict__["device_id"]).all()
        purchasing_information = db.query(models.PurchasingInformation).filter(
            models.PurchasingInformation.device_id == device.__dict__["device_id"]).one_or_none()
        return {"device": device, "owners": owners, "location": location, "purchasing_information": purchasing_information}
    return device


def get_owner_transaction(db: Session, owner_transaction_id: str):
    return db.query(models.OwnerTransaction).filter(models.OwnerTransaction.owner_transaction_id == owner_transaction_id).first()


def get_location_transaction(db: Session, location_transaction_id: str):
    return db.query(models.LocationTransaction).filter(models.LocationTransaction.location_transaction_id == location_transaction_id).first()


def get_purchasing_information(db: Session, purchasing_information_id: str):
    return db.query(models.PurchasingInformation).filter(models.PurchasingInformation.purchasing_information_id == purchasing_information_id).first()


# GET List of Entries

def get_users(db: Session, skip: int = 0, limit: int = 100):
    query = db.query(models.User)
    query = query.offset(skip).limit(limit).all()
    return query


def get_devices(db: Session, skip: int = 0, limit: int = 100, show_owners: bool = False):
    query = db.query(models.Device)
    query = query.offset(skip).limit(limit).all()

    if show_owners and len(query) > 0:
        device_and_owner = []
        for device in query:
            device_id = device.__dict__["device_id"]
            # Source .scalar(): https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.scalar
            # Source max(): https://docs.sqlalchemy.org/en/14/core/functions.html
            max_timestamp = db.query(func.max(models.OwnerTransaction.timestamp_owner_since)).filter(
                models.OwnerTransaction.device_id == device_id
            ).scalar()

            highest_timestamp_owner = db.query(models.OwnerTransaction).filter(
                models.OwnerTransaction.device_id == device_id,
                models.OwnerTransaction.timestamp_owner_since == max_timestamp
            ).first()

            device_and_owner.append([device, highest_timestamp_owner])
        return device_and_owner

    return query


def get_owner_transactions(db: Session, skip: int = 0, limit: int = 100):
    query = db.query(models.OwnerTransaction)
    query = query.offset(skip).limit(limit).all()
    return query


def get_location_transactions(db: Session, skip: int = 0, limit: int = 100):
    query = db.query(models.LocationTransaction)
    query = query.offset(skip).limit(limit).all()
    return query


def get_purchasing_information_all(db: Session, skip: int = 0, limit: int = 100):
    query = db.query(models.PurchasingInformation)
    query = query.offset(skip).limit(limit).all()
    return query

# GET List by device_id

def get_all_owner_transactions_for_device(db: Session, device_id, skip: int = 0, limit: int = 100):
    query = db.query(models.OwnerTransaction).filter(models.OwnerTransaction.device_id == device_id)
    query = query.offset(skip).limit(limit).all()
    return query

def get_all_location_transactions_for_device(db: Session, device_id, skip: int = 0, limit: int = 100):
    query = db.query(models.LocationTransaction).filter(models.LocationTransaction.device_id == device_id)
    query = query.offset(skip).limit(limit).all()
    return query


def get_purchasing_information_for_device(db: Session, device_id):
    query = db.query(models.PurchasingInformation).filter(models.PurchasingInformation.device_id == device_id).first()
    return query