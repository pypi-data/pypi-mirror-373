from akron import akron
from akron.models import ModelMixin
from pydantic import BaseModel
import pytest

class User(BaseModel, ModelMixin):
    id: int
    name: str
    age: int

@pytest.fixture(scope="module")
def sqlite_db():
    db = akron("sqlite:///:memory:")
    User.create_table(db)
    yield db
    db.close()

def test_insert_and_find(sqlite_db):
    User.insert(sqlite_db, User(id=1, name="Alice", age=30))
    users = User.find(sqlite_db)
    assert any(u.name == "Alice" for u in users)

def test_update(sqlite_db):
    User.insert(sqlite_db, User(id=2, name="Bob", age=25))
    updated = User.update(sqlite_db, {"id": 2}, {"age": 26})
    assert updated > 0
    users = User.find(sqlite_db, {"id": 2})
    assert users[0].age == 26

def test_delete(sqlite_db):
    User.insert(sqlite_db, User(id=3, name="Charlie", age=22))
    deleted = User.delete(sqlite_db, {"id": 3})
    assert deleted > 0
    users = User.find(sqlite_db, {"id": 3})
    assert len(users) == 0
