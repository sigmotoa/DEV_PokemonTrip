import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine, SQLModel
from fastapi import FastAPI, Depends
from typing import Annotated

load_dotenv()
clever_db = os.getenv("CLEVER_URI")
neon_db = os.getenv("DATABASE_URL_NEON")

sqlite_name="pokedex.sqlite3"
sqlite_url=(f"sqlite:///{sqlite_name}")

engine = create_engine(neon_db)


def create_all_tables(app: FastAPI):
    if os.getenv("ENV") == "dev":
        SQLModel.metadata.create_all(engine)
    yield 


def get_session()->Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

