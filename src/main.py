from collections.abc import AsyncGenerator

from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from src.rota.rotas import add_user_to_rota_on_date, get_rota_between, Rota_Assignment
from src.db.db import DB, DEFAULT_TABLE_SCHEMA
from datetime import date, datetime


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    db = DB(DEFAULT_TABLE_SCHEMA, "./data")
    app.state.db = db
    yield
    db.close()


app = FastAPI(lifespan=lifespan)


def get_db() -> DB:
    return app.state.db


@app.get("/")
def main() -> str:
    return "hello world"


@app.get("/rota", response_model=list[Rota_Assignment])
def get_rota_between_(
    start_date: date,
    end_date: date,
    rota_id: int,
    db: DB = Depends(get_db),
) -> list[Rota_Assignment]:
    try:
        return get_rota_between(start_date, end_date, rota_id, db.get_db())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rota")
def add_user_to_rota_(
    user_id: int,
    rota_id: int,
    date: datetime,
    db: DB = Depends(get_db),
) -> None:
    try:
        add_user_to_rota_on_date(user_id, rota_id, date, db)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
