from src.rotas import load_db
from src.rotas import get_on_call_between
from datetime import date


load_db(
    ["users", "rotas", "change_dates", "rota_snapshots", "overrides"],
    "./data"
)
print(get_on_call_between(date(2025,1,1), date(2025,10,1), 0))