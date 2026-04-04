from pathlib import Path
from typing import Generator

import pytest
import shutil
from src.db.db import DB, DEFAULT_TABLE_LIST

TEST_DB_DIRECTORY = "./test/test_db_data"

@pytest.fixture(scope="session")
def shared_db() -> Generator[DB]:
    db = DB(DEFAULT_TABLE_LIST, TEST_DB_DIRECTORY)

    yield db

    db.close()

@pytest.fixture()
def fresh_db(tmp_path: Path) -> Generator[DB]:
    shutil.copytree(TEST_DB_DIRECTORY, tmp_path, dirs_exist_ok = True)
    db = DB(DEFAULT_TABLE_LIST, str(tmp_path))

    yield db

    db.close()