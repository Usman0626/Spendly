import importlib

import pytest
import database.db as db


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test_expense_tracker.db"))
    db.init_db()
    yield db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test_expense_tracker.db"))
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client
