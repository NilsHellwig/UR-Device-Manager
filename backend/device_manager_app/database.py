from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event

SQLALCHEMY_DATABASE_URL = 'sqlite:///./device_manager_app.db'


# Sources to write this handler: https://docs.sqlalchemy.org/en/14/core/event.html / (enforce foreign key constraint) https://www.sqlite.org/pragma.html
def enforce_foreign_key(dbapi_conn, conn_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
event.listen(engine, "connect", enforce_foreign_key)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
