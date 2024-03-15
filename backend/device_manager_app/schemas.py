from pydantic import BaseModel
from typing import Union, Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    rz_username: str


class User(BaseModel):
    rz_username: str
    organisation_unit: str
    full_name: str

    class Config:
        orm_mode = True


class UserCreate(User):
    password: str
    pass


class UserGet(User):
    has_admin_privileges: bool
    pass


class Device(BaseModel):
    title: str
    device_type: str
    # Source: https://docs.pydantic.dev/usage/types/
    description: Union[str, None]
    accessories: Union[str, None]
    serial_number: str
    rz_username_buyer: str

    class Config:
        orm_mode = True


class DevicePost(Device):
    rz_username_owner: str
    room_code: str
    cost_centre: int
    seller: Union[str, None]
    timestamp_warranty_end: int
    timestamp_purchase: int
    price: str
    uploaded_device_image: Optional[str]
    pass


class DeviceGet(Device):
    device_id: str
    pass


class DeviceUpdate(BaseModel):
    title: Optional[Union[str, None]]
    device_type: Optional[Union[str, None]]
    description: Optional[Union[str, None]]
    accessories: Optional[Union[str, None]]
    serial_number: Optional[Union[str, None]]
    rz_username_buyer: Optional[Union[str, None]]
    uploaded_device_image: Optional[str]

    class Config:
        # Source "forbid": https://docs.pydantic.dev/usage/model_config/
        extra = 'forbid'


class OwnerTransaction(BaseModel):
    rz_username: str
    device_id: str

    class Config:
        orm_mode = True


class OwnerTransactionGet(OwnerTransaction):
    owner_transaction_id: str
    timestamp_owner_since: int
    pass


class OwnerTransactionUpdate(BaseModel):
    rz_username: Optional[Union[str, None]]
    timestamp_owner_since: Optional[Union[int, None]]

    class Config:
        # Source "forbid": https://docs.pydantic.dev/usage/model_config/
        extra = 'forbid'


class LocationTransaction(BaseModel):
    room_code: str
    device_id: str

    class Config:
        orm_mode = True


class LocationTransactionGet(LocationTransaction):
    location_transaction_id: str
    timestamp_located_since: int
    pass


class LocationTransactionUpdate(BaseModel):
    location_transaction_id: Optional[Union[str, None]]
    timestamp_located_since: Optional[Union[int, None]]
    room_code: Optional[Union[str, None]]

    class Config:
        # Source "forbid": https://docs.pydantic.dev/usage/model_config/
        extra = 'forbid'


class PurchasingInformation(BaseModel):
    price: str
    timestamp_warranty_end: int
    timestamp_purchase: int
    cost_centre: int
    seller: str
    device_id: str

    class Config:
        orm_mode = True


class PurchasingInformationUpdate(BaseModel):
    price: Optional[Union[str, None]]
    timestamp_warranty_end: Optional[Union[int, None]]
    timestamp_purchase: Optional[Union[int, None]]
    cost_centre: Optional[Union[int, None]]
    seller: Optional[Union[str, None]]

    class Config:
        # Source "forbid": https://docs.pydantic.dev/usage/model_config/
        extra = 'forbid'


class PurchasingInformationGet(PurchasingInformation):
    purchasing_information_id: str
    pass
