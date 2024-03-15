from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from .constants import key_to_german_label
from sqlalchemy.orm import relationship, validates
from fastapi import HTTPException
from .database import Base
import json
import os


class User(Base):
    __tablename__ = 'users'

    rz_username = Column(String, primary_key=True)
    full_name = Column(String)
    organisation_unit = Column(String)
    hashed_password = Column(String)
    has_admin_privileges = Column(Boolean)


class Device(Base):
    __tablename__ = 'devices'

    device_id = Column(String, primary_key=True)
    title = Column(String)
    device_type = Column(String)
    description = Column(String, nullable=True)
    accessories = Column(String, nullable=True)
    serial_number = Column(String)
    rz_username_buyer = Column(String)
    image_url = Column(String)

    # Learned about it here: https://docs.sqlalchemy.org/en/20/orm/mapped_attributes.html#simple-validators
    @validates("device_type")
    def validate_device_type(self, key, value):
        if not(value in ["projektor", "computer", "laptop", "mikrofon", "whiteboard", "unbekannt"]):
            raise HTTPException(
                status_code=404, detail=f'{value} ist keine valider Wert für den Gerätetyp.')
        return value

    @validates("title", "serial_number", "rz_username_buyer")
    def validate_length(self, key, value):
        if len(value) == 0:
            raise HTTPException(
                status_code=404, detail=f'{key_to_german_label[key]} muss mindestens ein Zeichen lang sein.')
        return value

    owner_transactions = relationship('OwnerTransaction', back_populates='devices',
                                      cascade='all, delete-orphan')
    location_transactions = relationship('LocationTransaction', back_populates='devices',
                                         cascade='all, delete-orphan')
    purchasing_information = relationship('PurchasingInformation', back_populates='devices',
                                          cascade='all, delete-orphan')


class OwnerTransaction(Base):
    __tablename__ = "owner_transactions"

    owner_transaction_id = Column(String, primary_key=True)
    rz_username = Column(String)
    timestamp_owner_since = Column(Integer)

    @validates("rz_username")
    def validate_username(self, key, value):
        if len(value) == 0:
            raise HTTPException(
                status_code=404, detail=f'{key_to_german_label[key]} muss mindestens ein Zeichen lang sein.')
        return value

    @validates("timestamp_owner_since")
    def validate_timestamp(self, key, value):
        if not isinstance(value, int) and not isinstance(value, float):
            raise HTTPException(
                status_code=404, detail=f'{key_to_german_label[key]} muss mindestens eine Ganzzahl lang sein')
        return value

    device_id = Column(String, ForeignKey('devices.device_id'))
    devices = relationship('Device', back_populates='owner_transactions')


class LocationTransaction(Base):
    __tablename__ = "location_transactions"

    location_transaction_id = Column(String, primary_key=True)
    room_code = Column(String)
    timestamp_located_since = Column(Integer)

    @validates("room_code")
    def validate_room_code(self, key, value):
        file = open("device_manager_app/data/hoersaal_raumcode.json", "r")
        rooms = json.load(file)
        file.close()
        room_codes = []
        for room in rooms:
            room_codes.append(room['room_code'])
        if not(value in room_codes):
            raise HTTPException(
                status_code=404, detail=f'Dies ist keine valide Raumnummer.')
        return value

    @validates("timestamp_located_since")
    def validate_length(self, key, value):
        if not isinstance(value, int) and not isinstance(value, float):
            raise HTTPException(
                status_code=404, detail=f'{key_to_german_label[key]} muss mindestens eine Ganzzahl lang sein.')
        return value

    device_id = Column(String, ForeignKey('devices.device_id'))
    devices = relationship('Device', back_populates='location_transactions')


class PurchasingInformation(Base):
    __tablename__ = "purchasing_information"

    purchasing_information_id = Column(String, primary_key=True)
    price = Column(String)
    timestamp_warranty_end = Column(Integer)
    timestamp_purchase = Column(Integer)
    cost_centre = Column(Integer)
    seller = Column(String, nullable=True)

    @validates("timestamp_warranty_end", "timestamp_purchase")
    def check_if_valid_unix_timecode(self, key, value):
        if not isinstance(value, int) and not isinstance(value, float):
            raise HTTPException(
                status_code=404, detail=f'{key_to_german_label[key]} muss mindestens eine Ganzzahl lang sein.')
        return value

    @validates("cost_centre")
    def validate_cost_centre(self, key, value):
        if isinstance(value, int) and len(str(value)) == 8:
           return value
        else:
           raise HTTPException(
            status_code=404, detail="Die Kostenstelle muss eine 8-stellige Zahl sein")


    @validates("price")
    def validate_length(self, key, text):
        if len(text) == 0:
            raise HTTPException(
                status_code=404, detail=f'{key_to_german_label[key]} muss mindestens ein Zeichen lang sein.')
        return text

    device_id = Column(String, ForeignKey('devices.device_id'))
    devices = relationship('Device', back_populates='purchasing_information')
