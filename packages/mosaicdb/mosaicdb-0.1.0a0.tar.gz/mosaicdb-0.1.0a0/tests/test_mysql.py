"""Test basic CRUD operations using Mosaic with MySQL."""

from mosaic import Mosaic

def run_example():
    # Update connection string as needed
    db = Mosaic("mysql://root:@localhost:3306/mosaic_test")

    # 1. Create table
    db.create_table("users", {"id": "int", "name": "str", "age": "int"})

    # 2. Insert rows
    alice_id = db.insert("users", {"name": "Alice", "age": 30})
    bob_id = db.insert("users", {"name": "Bob", "age": 25})
    print("inserted ids:", alice_id, bob_id)

    # 3. Read all
    all_users = db.find("users")
    print("all users:", all_users)

    # 4. Filtered read
    young = db.find("users", {"age": 25})
    print("age=25:", young)

    # 5. Update
    updated = db.update("users", {"id": alice_id}, {"age": 31})
    print("rows updated:", updated)
    print("after update:", db.find("users", {"id": alice_id}))

    # 6. Delete
    deleted = db.delete("users", {"id": bob_id})
    print("rows deleted:", deleted)
    print("final:", db.find("users"))

    db.close()

if __name__ == "__main__":
    run_example()
