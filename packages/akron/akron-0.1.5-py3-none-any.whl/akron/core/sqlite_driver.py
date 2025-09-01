"""SQLite driver for akron."""

import sqlite3
from typing import Dict, Any, Optional, List, Tuple
from .base import BaseDriver
from ..utils import map_type, sanitize_identifier
from ..exceptions import AkronError, TableNotFoundError


class SQLiteDriver(BaseDriver):
    def __init__(self, db_url: str):
        """db_url format: sqlite:///path/to/db or sqlite:///:memory:"""
        if not db_url.startswith("sqlite://"):
            raise AkronError("SQLiteDriver requires sqlite:// URL")
        # support sqlite:///file.db and sqlite:///:memory:
        path = db_url.replace("sqlite://", "")
        # when path empty -> default to akron.db
        if path in ("", "/"):
            path = "akron.db"
        # handle in-memory database for both ':memory:' and '/:memory:'
        if path in (":memory:", "/:memory:"):
            self._path = ":memory:"
            self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self._path = path
            self.conn = sqlite3.connect(self._path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def _exec(self, sql: str, params: Tuple = ()):
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            # common: no such table
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        """
        Create a table with optional foreign keys.
        Foreign key syntax: 'type->table.column'
        Example: {"user_id": "int->users.id"}
        """
        if not schema or not isinstance(schema, dict):
            raise AkronError("schema must be a non-empty dict")

        tname = sanitize_identifier(table_name)
        cols = []
        fks = []
        for col, dtype in schema.items():
            cname = sanitize_identifier(col)
            # Check for FK syntax
            if isinstance(dtype, str) and "->" in dtype:
                base_type, fk = dtype.split("->", 1)
                sql_type = map_type(base_type.strip())
                ref_table, ref_col = fk.strip().split(".")
                ref_table = sanitize_identifier(ref_table)
                ref_col = sanitize_identifier(ref_col)
                cols.append(f"{cname} {sql_type}")
                fks.append(f"FOREIGN KEY({cname}) REFERENCES {ref_table}({ref_col})")
            else:
                sql_type = map_type(dtype)
                if cname == "id" and sql_type.upper() == "INTEGER":
                    cols.append(f"{cname} {sql_type} PRIMARY KEY AUTOINCREMENT")
                else:
                    cols.append(f"{cname} {sql_type}")
        cols_sql = ", ".join(cols + fks)
        sql = f"CREATE TABLE IF NOT EXISTS {tname} ({cols_sql})"
        self._exec(sql)

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        if not data or not isinstance(data, dict):
            raise AkronError("data must be a non-empty dict")
        tname = sanitize_identifier(table_name)
        keys = [sanitize_identifier(k) for k in data.keys()]
        placeholders = ", ".join(["?"] * len(keys))
        cols_sql = ", ".join(keys)
        sql = f"INSERT INTO {tname} ({cols_sql}) VALUES ({placeholders})"
        params = tuple(data.values())
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                raise AkronError(f"Duplicate entry on unique field: {msg}")
            if "FOREIGN KEY constraint failed" in msg:
                raise AkronError(f"Foreign key constraint failed: {msg}")
            raise AkronError(msg)
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        return self.cur.lastrowid

    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        tname = sanitize_identifier(table_name)
        sql = f"SELECT * FROM {tname}"
        params: Tuple = ()
        if filters:
            if not isinstance(filters, dict):
                raise akronError("filters must be a dict")
            conds = []
            for k in filters.keys():
                conds.append(f"{sanitize_identifier(k)} = ?")
            sql += " WHERE " + " AND ".join(conds)
            params = tuple(filters.values())

        try:
            self.cur.execute(sql, params)
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))

        columns = [d[0] for d in self.cur.description] if self.cur.description else []
        rows = self.cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        if not filters or not isinstance(filters, dict):
            raise AkronError("filters must be a non-empty dict for update")
        if not new_values or not isinstance(new_values, dict):
            raise AkronError("new_values must be a non-empty dict for update")
        tname = sanitize_identifier(table_name)
        set_clause = ", ".join(f"{sanitize_identifier(k)} = ?" for k in new_values.keys())
        where_clause = " AND ".join(f"{sanitize_identifier(k)} = ?" for k in filters.keys())
        sql = f"UPDATE {tname} SET {set_clause} WHERE {where_clause}"
        params = tuple(new_values.values()) + tuple(filters.values())
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        return self.cur.rowcount

    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        if not filters or not isinstance(filters, dict):
            raise AkronError("filters must be a non-empty dict for delete")
        tname = sanitize_identifier(table_name)
        where_clause = " AND ".join(f"{sanitize_identifier(k)} = ?" for k in filters.keys())
        sql = f"DELETE FROM {tname} WHERE {where_clause}"
        params = tuple(filters.values())
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        return self.cur.rowcount

    def close(self):
        try:
            self.cur.close()
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass
