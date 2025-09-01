import pytest
from akron import Akron

@pytest.fixture(scope="module")
def mysql_db():
    db = Akron("mysql://root:@localhost:3306/akron_test")
    yield db
    db.close()

def test_create_and_insert(mysql_db):
    mysql_db.create_table("users", {"id": "int", "name": "str", "age": "int"})
    user_id = mysql_db.insert("users", {"name": "Alice", "age": 30})
    assert user_id is not None
    users = mysql_db.find("users")
    assert any(u["name"] == "Alice" for u in users)

def test_update(mysql_db):
    mysql_db.insert("users", {"name": "Bob", "age": 25})
    updated = mysql_db.update("users", {"name": "Bob"}, {"age": 26})
    assert updated > 0
    users = mysql_db.find("users", {"name": "Bob"})
    assert users[0]["age"] == 26

def test_delete(mysql_db):
    mysql_db.insert("users", {"name": "Charlie", "age": 22})
    deleted = mysql_db.delete("users", {"name": "Charlie"})
    assert deleted > 0
    users = mysql_db.find("users", {"name": "Charlie"})
    assert len(users) == 0

def test_multi_table_fk(mysql_db):
    mysql_db.create_table("users", {"id": "int", "name": "str"})
    mysql_db.create_table("orders", {"id": "int", "user_id": "int->users.id", "amount": "float"})
    alice_id = mysql_db.insert("users", {"name": "Alice"})
    order_id = mysql_db.insert("orders", {"user_id": alice_id, "amount": 100.0})
    orders = mysql_db.find("orders", {"user_id": alice_id})
    assert any(o["amount"] == 100.0 for o in orders)
    # FK constraint test
    with pytest.raises(Exception):
        mysql_db.insert("orders", {"user_id": 999, "amount": 10.0})
