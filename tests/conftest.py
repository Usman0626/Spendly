import pytest
import database.db as db


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test_expense_tracker.db"))
    db.init_db()
    yield db
