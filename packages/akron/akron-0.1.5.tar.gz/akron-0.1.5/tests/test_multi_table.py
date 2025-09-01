"""Test multi-table and foreign key support in akron (MySQL example)."""

from akron import Akron

def run_example():
    # db = Akron("mysql://root:@localhost:3306/akron_test")
    db = Akron("sqlite://test.db")

    # Drop tables if they exist (for clean test)
    try:
        db.driver.cur.execute("DROP TABLE IF EXISTS orders")
        db.driver.cur.execute("DROP TABLE IF EXISTS users")
        db.driver.conn.commit()
    except Exception:
        pass

    # Create users table
    db.create_table("users", {
        "id": "int",
        "name": "str"
    })

    # Create orders table with foreign key to users.id
    db.create_table("orders", {
        "id": "int",
        "user_id": "int->users.id",
        "amount": "float"
    })

    # Insert users
    alice_id = db.insert("users", {"name": "Alice"})
    bob_id = db.insert("users", {"name": "Bob"})

    # Insert orders
    order1 = db.insert("orders", {"user_id": alice_id, "amount": 100.0})
    order2 = db.insert("orders", {"user_id": bob_id, "amount": 50.0})
    order3 = db.insert("orders", {"user_id": alice_id, "amount": 75.0})

    print("Users:", db.find("users"))
    print("Orders:", db.find("orders"))

    # Try inserting an order with invalid user_id (should fail)
    try:
        db.insert("orders", {"user_id": 999, "amount": 10.0})
    except Exception as e:
        print("Expected FK error:", e)

    db.close()

if __name__ == "__main__":
    run_example()
