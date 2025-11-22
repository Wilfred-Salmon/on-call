import pytest
import shutil
from src.db import build_db, DEFAULT_TABLE_LIST

TEST_DB_DIRECTORY = "./test/test_db_data"

@pytest.fixture(scope="session")
def shared_db():
    db = build_db(DEFAULT_TABLE_LIST, TEST_DB_DIRECTORY)

    yield db

    db.close()

@pytest.fixture()
def fresh_db(tmp_path):
    shutil.copytree(TEST_DB_DIRECTORY, tmp_path, dirs_exist_ok = True)
    db = build_db(DEFAULT_TABLE_LIST, tmp_path)

    yield db

    db.close()