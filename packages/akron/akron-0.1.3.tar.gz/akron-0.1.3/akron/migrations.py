"""Akron migration manager: auto schema tracking and migrations."""
import json
import os
from typing import Dict, Any, List

class MigrationManager:
    def __init__(self, db, migrations_dir="migrations"):
        self.db = db
        self.migrations_dir = migrations_dir
        os.makedirs(migrations_dir, exist_ok=True)

    def _get_schema(self, table_name: str) -> Dict[str, Any]:
        driver = self.db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            # SQL: get columns and types
            driver.cur.execute(f"PRAGMA table_info({table_name})")
            return {row[1]: row[2] for row in driver.cur.fetchall()}
        elif hasattr(driver, "db"):
            doc = driver.db[table_name].find_one()
            return doc if doc else {}
        return {}

    def _diff_schema(self, from_schema: Dict[str, Any], to_schema: Dict[str, Any]):
        # Returns list of migration steps
        steps = []
        # Additions
        for col, col_type in to_schema.items():
            if col not in from_schema:
                steps.append({"action": "add", "column": col, "type": col_type})
        # Removals
        for col in from_schema:
            if col not in to_schema:
                steps.append({"action": "remove", "column": col})
        # Type changes
        for col, col_type in to_schema.items():
            if col in from_schema and from_schema[col] != col_type:
                steps.append({"action": "change_type", "column": col, "from": from_schema[col], "to": col_type})
        # Renames (not auto-detectable, user must specify in future)
        return steps
    def makemigrations(self, table_name: str, new_schema: Dict[str, Any]):
        current_schema = self._get_schema(table_name)
        steps = self._diff_schema(current_schema, new_schema)
        migration = {
            "table": table_name,
            "from": current_schema,
            "to": new_schema,
            "steps": steps
        }
        fname = f"{self.migrations_dir}/{table_name}_migration.json"
        with open(fname, "w") as f:
            json.dump(migration, f, indent=2)
        print(f"Migration for {table_name} saved to {fname}")

    def migrate(self, table_name: str):
        fname = f"{self.migrations_dir}/{table_name}_migration.json"
        if not os.path.exists(fname):
            print(f"No migration file for {table_name}")
            return
        with open(fname) as f:
            migration = json.load(f)
        driver = self.db.driver
        steps = migration["steps"]
        # Create migration history table if not exists
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute("CREATE TABLE IF NOT EXISTS _akron_migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT, migration_file TEXT, applied_at TEXT)")
            driver.conn.commit()
            try:
                driver.conn.execute("BEGIN")
                for step in steps:
                    if step["action"] == "add":
                        sql_type = step["type"].upper()
                        driver.cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {step['column']} {sql_type}")
                    elif step["action"] == "remove":
                        # SQLite does not support DROP COLUMN directly; workaround needed for production
                        print(f"Column removal not supported natively in SQLite. Manual intervention required for {step['column']}")
                    elif step["action"] == "change_type":
                        print(f"Type change for column {step['column']} from {step['from']} to {step['to']} not supported natively. Manual intervention required.")
                driver.conn.commit()
                driver.cur.execute("INSERT INTO _akron_migrations (table_name, migration_file, applied_at) VALUES (?, ?, datetime('now'))", (table_name, fname))
                driver.conn.commit()
                print(f"Migrated {table_name} to new schema.")
            except Exception as e:
                driver.conn.rollback()
                print(f"Migration failed and rolled back: {e}")
        elif hasattr(driver, "db"):
            print(f"MongoDB is schemaless; no migration needed for {table_name}.")
