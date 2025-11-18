import pytest
from src.db import build_db, DEFAULT_TABLE_LIST

@pytest.fixture(scope="session")
def shared_db():
    db = build_db(DEFAULT_TABLE_LIST, "./test/test_data")

    yield db

    db.close()

def fresh_db():
    db = build_db(DEFAULT_TABLE_LIST, "./test/test_data")

    yield db

    db.close()