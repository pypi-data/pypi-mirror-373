import pytest
from akron import Akron

@pytest.fixture(scope="module")
def mongo_db():
    db = Akron("mongodb://localhost:27017/akron_test")
    yield db
    db.close()

def test_create_and_insert(mongo_db):
    mongo_db.create_table("users", {"id": "int", "name": "str"})
    user_id = mongo_db.insert("users", {"id": 1, "name": "Alice"})
    assert user_id is not None
    users = mongo_db.find("users")
    assert any(u["name"] == "Alice" for u in users)

def test_update(mongo_db):
    mongo_db.insert("users", {"id": 2, "name": "Bob"})
    updated = mongo_db.update("users", {"id": 2}, {"name": "Bobby"})
    assert updated > 0
    users = mongo_db.find("users", {"id": 2})
    assert users[0]["name"] == "Bobby"

def test_delete(mongo_db):
    mongo_db.insert("users", {"id": 3, "name": "Charlie"})
    deleted = mongo_db.delete("users", {"id": 3})
    assert deleted > 0
    users = mongo_db.find("users", {"id": 3})
    assert len(users) == 0
