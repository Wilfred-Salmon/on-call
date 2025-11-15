from src.rotas import load_db
from src.rotas import get_rota_between
from datetime import date

load_db(
    ["users", "rotas", "change_dates", "rota_snapshots", "overrides"],
    "./data"
)
print(get_rota_between(date(2025,1,1), date(2025,10,1), 0))