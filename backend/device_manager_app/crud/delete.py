from fastapi import HTTPException, Response
from sqlalchemy.orm import Session
from .. import models


def delete_database(db: Session):
    db.query(models.OwnerTransaction).delete()
    db.query(models.LocationTransaction).delete()
    db.query(models.PurchasingInformation).delete()
    db.query(models.Device).delete()
    db.commit()


def delete_user(db: Session, rz_username: str):
    user = db.query(models.User).filter(
        models.User.rz_username == rz_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()
    return Response(status_code=204)


def delete_device(db: Session, device_id: str):
    device = db.query(models.Device).filter(
        models.Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found.")
    db.delete(device)
    db.commit()
    return Response(status_code=204)


def delete_owner_transaction(db: Session, owner_transaction_id: str):
    owner_transaction = db.query(models.OwnerTransaction).filter(
        models.OwnerTransaction.owner_transaction_id == owner_transaction_id).first()
    if not owner_transaction:
        raise HTTPException(
            status_code=404, detail="OwnerTransaction not found.")
    db.delete(owner_transaction)
    db.commit()
    return Response(status_code=204)


def delete_location_transaction(db: Session, location_transaction_id: str):
    location_transaction = db.query(models.LocationTransaction).filter(
        models.LocationTransaction.location_transaction_id == location_transaction_id).first()
    if not location_transaction:
        raise HTTPException(
            status_code=404, detail="LocationTransaction not found.")
    db.delete(location_transaction)
    db.commit()
    return Response(status_code=204)


def delete_purchasing_information(db: Session, purchasing_information_id: str):
    purchasing_information = db.query(models.PurchasingInformation).filter(
        models.PurchasingInformation.purchasing_information_id == purchasing_information_id).first()
    if not purchasing_information:
        raise HTTPException(
            status_code=404, detail="PurchasingInformation not found.")
    db.delete(purchasing_information)
    db.commit()
    return Response(status_code=204)
