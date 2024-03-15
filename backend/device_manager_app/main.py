from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request
from starlette.concurrency import iterate_in_threadpool
from .database import SessionLocal, engine
from .crud import delete, get, post, update
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from passlib.context import CryptContext
from . import models, schemas, settings
from .database import SessionLocal
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Union
from typing import List
from .schemas import *
import time
import os

# 1. Setup Database


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


models.Base.metadata.create_all(bind=engine)


# 2. Setup Router
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/

app = FastAPI()

# Source: https://fastapi.tiangolo.com/tutorial/cors/
origins = [
    "http://localhost:3000",
]

app = FastAPI(title="Device Manager API",
              version="1.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")

# 3. Setup Authentication
# I followed this tutorial (official documentation): https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def authenticate_user(db_user, password: str):
    if not pwd_context.verify(password, db_user.hashed_password):
        return False
    return True


def get_user_from_token(token, db):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        rz_username: str = payload.get("sub")
        if rz_username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    db_user = get.get_user(db=db, rz_username=rz_username)
    return db_user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    db_user = get_user_from_token(token, db)
    return db_user


def get_current_user_with_admin_only(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    db_user = get_user_from_token(token, db)

    if db_user.has_admin_privileges == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin privileges required")
    return db_user

# 4. Add two users admin/user


def run_operation_once_at_startup():
    db = SessionLocal()
    try:
        db_user = models.User(rz_username="admin", has_admin_privileges=True,
                              full_name="Administrator", organisation_unit="Rechenzentrum", hashed_password=get_password_hash(settings.ADMIN_PASSWORD))
        db.add(db_user)
        db_user = models.User(rz_username="user", has_admin_privileges=False,
                              full_name="Beispiel Nutzer", organisation_unit="Fakultät für Informatik und Data Science", hashed_password=get_password_hash(settings.TEST_STANDARD_USER_PASSWORD))
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except:
        pass

    db.close()


run_operation_once_at_startup()


# 5. Define Routes

# Image Serving - Route
# Source: https://fastapi.tiangolo.com/tutorial/static-files/



if not os.path.exists(settings.PUBLIC_IMAGES_DIR):
    os.makedirs(settings.PUBLIC_IMAGES_DIR)


app.mount("/static", StaticFiles(directory=settings.PUBLIC_IMAGES_DIR), name="static")


# AUTH-ROUTES


@router.post("/login", response_model=Token, tags=["Authentication"])
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = get.get_user(db=db, rz_username=form_data.username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="RZ-Username")
    is_authorized = authenticate_user(
        db_user, form_data.password)
    if not(is_authorized):
        raise HTTPException(status_code=404, detail="Passwort")
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.rz_username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.User, status_code=201, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    return post.create_user(db=db, user=user, hashed_password=get_password_hash(user.password))


@router.get("/check_auth", response_model=schemas.UserGet, tags=["Authentication"])
def check_auth(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user

# Database import/export/purge


@router.post("/import", status_code=201, tags=["Database Import/Export/Purge"])
def import_database(database: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    post.import_database(db, database)
    return {"message": "successfully imported all tables"}


@router.get("/export", status_code=200, tags=["Database Import/Export/Purge"])
def export_database(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    database_dict = get.export_database(db)
    return database_dict


@router.delete("/purge", status_code=204, tags=["Database Import/Export/Purge"])
def delete_database(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    delete.delete_database(db)
    return {"message": "successfully deleted all tables"}

# POST-ROUTES

# Hint: Since it should not be possible to add a device without information about the purchase,
# location and owner, we must also store this information in the corresponding tables.


@router.post("/devices", response_model=schemas.DeviceGet, status_code=201, tags=["Devices"])
def create_device(new_device_data: schemas.DevicePost, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post.create_device(db=db, new_device_data=new_device_data)


@router.post("/owner_transactions", response_model=schemas.OwnerTransactionGet, status_code=201, tags=["OwnerTransactions"])
def create_owner_transaction(owner_transaction: schemas.OwnerTransaction, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post.create_owner_transaction(db=db, owner_transaction=owner_transaction)


@router.post("/location_transactions", response_model=schemas.LocationTransactionGet, status_code=201, tags=["LocationTransactions"])
def create_location_transaction(location_transaction: schemas.LocationTransaction, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post.create_location_transaction(db=db, location_transaction=location_transaction)


@router.post("/purchasing_information", response_model=schemas.PurchasingInformationGet, status_code=201, tags=["PurchasingInformation"])
def create_purchasing_information(purchasing_information: schemas.PurchasingInformation, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post.create_purchasing_information(db=db, purchasing_information=purchasing_information)

# GET-ROUTES: List


@router.get("/users", response_model=List[schemas.UserGet], tags=["Users"])
def get_users(skip: int = 0, limit: int = settings.GET_ALL_DEFAULT_LIMIT, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    users = get.get_users(
        db, skip=skip, limit=limit)
    return users


@router.get("/devices", tags=["Devices"])
def get_devices(skip: int = 0, limit: int = settings.GET_ALL_DEFAULT_LIMIT, show_owners: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    devices = get.get_devices(
        db, skip=skip, limit=limit, show_owners=show_owners)
    return devices


@router.get("/owner_transactions", response_model=List[schemas.OwnerTransactionGet], tags=["OwnerTransactions"])
def get_owner_transactions(skip: int = 0, limit: int = settings.GET_ALL_DEFAULT_LIMIT, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = get.get_owner_transactions(
        db, skip=skip, limit=limit)
    return transactions


@router.get("/location_transactions", response_model=List[schemas.LocationTransactionGet], tags=["LocationTransactions"])
def get_location_transactions(skip: int = 0, limit: int = settings.GET_ALL_DEFAULT_LIMIT, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = get.get_location_transactions(
        db, skip=skip, limit=limit)
    return transactions


@router.get("/purchasing_information", response_model=List[schemas.PurchasingInformationGet], tags=["PurchasingInformation"])
def get_purchasing_information(skip: int = 0, limit: int = settings.GET_ALL_DEFAULT_LIMIT, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = get.get_purchasing_information_all(
        db, skip=skip, limit=limit)
    return transactions


# GET-Routes: List by device_id

@router.get("/devices/{device_id}/owner_transactions", response_model=List[schemas.OwnerTransactionGet], responses={404: {"description": "Device not found"}}, tags=["OwnerTransactions"])
def read_all_owner_transactions_for_device(device_id: str, skip: int = 0, limit: int = settings.GET_ALL_DEFAULT_LIMIT, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_owner_transactions = get.get_all_owner_transactions_for_device(
        db, device_id=device_id, skip=skip, limit=limit)
    if not db_owner_transactions:
        raise HTTPException(status_code=404, detail="Device not found.")
    return db_owner_transactions


@router.get("/devices/{device_id}/location_transactions", response_model=List[schemas.LocationTransactionGet], responses={404: {"description": "Device not found"}}, tags=["LocationTransactions"])
def read_all_location_transactions_for_device(device_id: str, skip: int = 0, limit: int = settings.GET_ALL_DEFAULT_LIMIT, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_location_transactions = get.get_all_location_transactions_for_device(
        db, device_id=device_id, skip=skip, limit=limit)
    if not db_location_transactions:
        raise HTTPException(status_code=404, detail="Device not found.")
    return db_location_transactions


@router.get("/devices/{device_id}/purchasing_information", response_model=schemas.PurchasingInformationGet, responses={404: {"description": "Device not found"}}, tags=["PurchasingInformation"])
def read_purchasing_information_for_device(device_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_purchasing_information = get.get_purchasing_information_for_device(
        db, device_id=device_id)
    if not db_purchasing_information:
        raise HTTPException(status_code=404, detail="Device not found.")
    return db_purchasing_information

# GET-Routes: Single Entries


@router.get('/users/{rz_username}', response_model=schemas.UserGet, responses={404: {"description": "User not found"}}, tags=["Users"])
def read_single_user(rz_username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    db_user = get.get_user(db, rz_username=rz_username)
    if not db_user:
        raise HTTPException(status_code=404, detail="Device not found.")
    return db_user


@router.get('/devices/{device_id}', responses={404: {"description": "Device not found"}}, tags=["Devices"])
def read_single_device(device_id: str, detailed_data: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_device = get.get_device(
        db, device_id=device_id, detailed_data=detailed_data)
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found.")
    return db_device


@router.get('/owner_transactions/{owner_transaction_id}', response_model=schemas.OwnerTransactionGet, responses={404: {"description": "OwnerTransaction not found"}}, tags=["OwnerTransactions"])
def read_single_owner_transaction(owner_transaction_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_owner_transaction = get.get_owner_transaction(
        db, owner_transaction_id=owner_transaction_id)
    if not db_owner_transaction:
        raise HTTPException(
            status_code=404, detail="OwnerTransaction not found.")
    return db_owner_transaction


@router.get('/location_transactions/{location_transaction_id}', response_model=schemas.LocationTransactionGet, responses={404: {"description": "LocationTransaction not found"}}, tags=["LocationTransactions"])
def read_single_location_transaction(location_transaction_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_location_transaction = get.get_location_transaction(
        db, location_transaction_id=location_transaction_id)
    if not db_location_transaction:
        raise HTTPException(
            status_code=404, detail="LocationTransaction not found.")
    return db_location_transaction


@router.get('/purchasing_information/{purchasing_information_id}', response_model=schemas.PurchasingInformationGet, responses={404: {"description": "PurchasingInformation not found"}}, tags=["PurchasingInformation"])
def read_single_purchasing_information(purchasing_information_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_purchasing_information = get.get_purchasing_information(
        db, purchasing_information_id=purchasing_information_id)
    if not db_purchasing_information:
        raise HTTPException(
            status_code=404, detail="PurchasingInformation not found.")
    return db_purchasing_information

# DELETE-Routes


@router.delete("/users/{rz_username}", response_model=schemas.UserGet, tags=["Users"])
def delete_user(rz_username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    deleted_user = delete.delete_user(db=db, rz_username=rz_username)
    return deleted_user


@router.delete("/devices/{device_id}", response_model=schemas.Device, tags=["Devices"])
def delete_device(device_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    deleted_device = delete.delete_device(db=db, device_id=device_id)
    return deleted_device


@router.delete("/owner_transactions/{owner_transaction_id}", response_model=schemas.OwnerTransactionGet, tags=["OwnerTransactions"])
def delete_owner_transaction(owner_transaction_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    deleted_owner_transaction = delete.delete_owner_transaction(
        db=db, owner_transaction_id=owner_transaction_id)
    return deleted_owner_transaction


@router.delete("/location_transactions/{location_transaction_id}", response_model=schemas.LocationTransactionGet, tags=["LocationTransactions"])
def delete_location_transaction(location_transaction_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    deleted_location_transaction = delete.delete_location_transaction(
        db=db, location_transaction_id=location_transaction_id)
    return deleted_location_transaction


@router.delete("/purchasing_information/{purchasing_information_id}", response_model=schemas.PurchasingInformationGet, tags=["PurchasingInformation"])
def delete_purchasing_information(purchasing_information_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    deleted_purchasing_information = delete.delete_purchasing_information(
        db=db, purchasing_information_id=purchasing_information_id)
    return deleted_purchasing_information


# UPDATE-Routes

@router.put("/devices/{device_id}", response_model=schemas.DeviceGet, tags=["Devices"])
def update_device(device_id: str, device: schemas.DeviceUpdate,  db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    updated_device = update.update_device(
        db=db, device_id=device_id, device=device, current_user=current_user)
    return updated_device


@router.put("/owner_transactions/{owner_transaction_id}", response_model=schemas.OwnerTransactionGet, tags=["OwnerTransactions"])
def update_owner_transaction(owner_transaction_id: str, owner_transaction: schemas.OwnerTransactionUpdate,  db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    updated_owner_transaction = update.update_owner_transaction(
        db=db, owner_transaction_id=owner_transaction_id, owner_transaction=owner_transaction)
    return updated_owner_transaction


@router.put("/location_transactions/{location_transaction_id}", response_model=schemas.LocationTransactionGet, tags=["LocationTransactions"])
def update_location_transaction(location_transaction_id: str, location_transaction: schemas.LocationTransactionUpdate,  db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    updated_location_transaction = update.update_location_transaction(
        db=db, location_transaction_id=location_transaction_id, location_transaction=location_transaction)
    return updated_location_transaction


@router.put("/purchasing_information/{purchasing_information_id}", response_model=schemas.PurchasingInformationGet, tags=["PurchasingInformation"])
def update_purchasing_information(purchasing_information_id: str, purchasing_information: schemas.PurchasingInformationUpdate,  db: Session = Depends(get_db), current_user: User = Depends(get_current_user_with_admin_only)):
    updated_purchasing_information = update.update_purchasing_information(
        db=db, purchasing_information_id=purchasing_information_id, purchasing_information=purchasing_information)
    return updated_purchasing_information

# 6. Add Logging

# Sources to write this logging middleware. It would be possible to additionally log the request body/ response body (see part that is commented)
# But in order not to save too many data, I have focussed on the essentials.
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/
# Source: https://github.com/encode/starlette/issues/874
# Source:  https://fastapi.tiangolo.com/tutorial/middleware/


@app.middleware("http")
async def log(request: Request, call_next):
    request_url = request.url.path
    start_request = time.time()
    response = await call_next(request)
    duration_request = time.time() - start_request

    # response_body = [section async for section in response.body_iterator]
    # response.body_iterator = iterate_in_threadpool(iter(response_body))

    # # extract information regarding response body/status code
    # response_body = response_body[0].decode()
    response_status_code = response.status_code

    file_path_logger = "./logger.csv"
    add_header = not(os.path.exists(file_path_logger))

    with open(file_path_logger, "a") as file:
        if add_header == True:
            file.write(
                "timestamp request,request route,request method,response code,duration in ms\n")
        file.write(str(time.ctime(time.time())) + "," + request_url + "," + request.method +
                   "," + str(response_status_code) + "," + str(duration_request*1000)+"\n")

    return response

app.include_router(router)
