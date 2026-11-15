import duckdb
import pytest

from src.config import DB_PATH
from src.pipeline import build, load_raw


@pytest.fixture(scope="session")
def raw():
    return load_raw()


@pytest.fixture(scope="session")
def con(raw):
    c = duckdb.connect(":memory:")
    build(c, raw)
    yield c
    c.close()
