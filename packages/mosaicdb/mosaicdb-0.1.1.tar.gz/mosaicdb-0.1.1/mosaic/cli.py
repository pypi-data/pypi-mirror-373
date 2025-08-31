"""Mosaic CLI for migration management."""
import argparse
from mosaic import Mosaic
from mosaic.migrations import MigrationManager
import sys


parser = argparse.ArgumentParser(description="Mosaic ORM CLI")
parser.add_argument("action", choices=[
    "makemigrations", "migrate", "showmigrations",
    "create-table", "drop-table", "inspect-schema", "seed", "raw-sql"
], help="Action")
parser.add_argument("table", nargs="?", help="Table name (if applicable)")
parser.add_argument("--db", required=True, help="Database URL (sqlite:///file.db, mysql://..., postgres://..., mongodb://...)")
parser.add_argument("--schema", help="Schema as JSON string for makemigrations/create-table")
parser.add_argument("--data", help="Seed data as JSON string")
parser.add_argument("--sql", help="Raw SQL to execute")

args = parser.parse_args()

def main():
    db = Mosaic(args.db)
    mgr = MigrationManager(db)
    import json
    if args.action == "makemigrations":
        if not args.schema:
            print("--schema required for makemigrations")
            sys.exit(1)
        schema = json.loads(args.schema)
        mgr.makemigrations(args.table, schema)
    elif args.action == "migrate":
        mgr.migrate(args.table)
    elif args.action == "showmigrations":
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute("SELECT * FROM _mosaic_migrations WHERE table_name=?", (args.table,))
            for row in driver.cur.fetchall():
                print(row)
        else:
            print("Migration history not supported for this backend.")
    elif args.action == "create-table":
        if not args.schema:
            print("--schema required for create-table")
            sys.exit(1)
        schema = json.loads(args.schema)
        db.create_table(args.table, schema)
        print(f"Table {args.table} created.")
    elif args.action == "drop-table":
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute(f"DROP TABLE IF EXISTS {args.table}")
            driver.conn.commit()
            print(f"Table {args.table} dropped.")
        elif hasattr(driver, "db"):
            driver.db.drop_collection(args.table)
            print(f"Collection {args.table} dropped.")
    elif args.action == "inspect-schema":
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute(f"PRAGMA table_info({args.table})")
            for row in driver.cur.fetchall():
                print(row)
        elif hasattr(driver, "db"):
            doc = driver.db[args.table].find_one()
            print(doc if doc else "No documents found.")
    elif args.action == "seed":
        if not args.data:
            print("--data required for seed")
            sys.exit(1)
        data = json.loads(args.data)
        db.insert(args.table, data)
        print(f"Seeded data into {args.table}.")
    elif args.action == "raw-sql":
        if not args.sql:
            print("--sql required for raw-sql")
            sys.exit(1)
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute(args.sql)
            if driver.cur.description:
                for row in driver.cur.fetchall():
                    print(row)
            driver.conn.commit()
            print("SQL executed.")
        else:
            print("Raw SQL not supported for this backend.")

if __name__ == "__main__":
    main()
