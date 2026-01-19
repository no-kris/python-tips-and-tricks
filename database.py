from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLACLHEMY_DB_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLACLHEMY_DB_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db
