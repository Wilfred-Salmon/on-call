from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from src.rota.rotas import get_rota_between, Rota_Assignment
from src.db.db import build_db, DEFAULT_TABLE_LIST
from datetime import date
from duckdb import DuckDBPyConnection

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = build_db(DEFAULT_TABLE_LIST, "./data")
    app.state.db = db
    
    yield
    
    db.close()

app = FastAPI(lifespan = lifespan)

def get_db():
    return app.state.db

@app.get("/")
def main() -> str:
    return "hello world"

@app.get("/rota", response_model = list[Rota_Assignment])
def get_rota_between_(
    start_date: date,
    end_date: date,
    rota_id: int,
    db: DuckDBPyConnection = Depends(get_db)
) -> list[Rota_Assignment]:
    try:
        return get_rota_between(start_date, end_date, rota_id, db)
    except ValueError as e:
        raise HTTPException(status_code = 400, detail = str(e))