"""MySQL driver for akron."""

import mysql.connector
from typing import Dict, Any, Optional, List, Tuple
from .base import BaseDriver
from ..exceptions import AkronError, TableNotFoundError

class MySQLDriver(BaseDriver):
    def __init__(self, db_url: str):
        """db_url format: mysql://user:password@host:port/dbname"""
        # Parse db_url
        import re
        pattern = r"mysql://(.*?):(.*?)@(.*?):(.*?)/(.*?)$"
        match = re.match(pattern, db_url)
        if not match:
            raise AkronError("Invalid MySQL URL format")
        user, password, host, port, database = match.groups()
        self.conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=int(port),
            database=database
        )
        self.cur = self.conn.cursor(dictionary=True)

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        cols = []
        fks = []
        for col, dtype in schema.items():
            # Foreign key syntax: 'type->table.column'
            if isinstance(dtype, str) and "->" in dtype:
                base_type, fk = dtype.split("->", 1)
                sql_type = "INT" if base_type.strip() == "int" else "VARCHAR(255)" if base_type.strip() == "str" else base_type.strip().upper()
                ref_table, ref_col = fk.strip().split(".")
                cols.append(f"{col} {sql_type}")
                fks.append(f"FOREIGN KEY({col}) REFERENCES {ref_table}({ref_col})")
            else:
                sql_type = "INT" if dtype == "int" else "VARCHAR(255)" if dtype == "str" else dtype.upper()
                if col == "id" and sql_type == "INT":
                    cols.append(f"{col} {sql_type} PRIMARY KEY AUTO_INCREMENT")
                else:
                    cols.append(f"{col} {sql_type}")
        cols_sql = ", ".join(cols + fks)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_sql})"
        self.cur.execute(sql)
        self.conn.commit()

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        keys = list(data.keys())
        placeholders = ", ".join(["%s"] * len(keys))
        cols_sql = ", ".join(keys)
        sql = f"INSERT INTO {table_name} ({cols_sql}) VALUES ({placeholders})"
        params = tuple(data.values())
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            msg = str(e)
            if "Duplicate entry" in msg or "1062" in msg:
                raise AkronError(f"Duplicate entry on unique field: {msg}")
            if "foreign key constraint fails" in msg or "1452" in msg:
                raise AkronError(f"Foreign key constraint failed: {msg}")
            raise AkronError(msg)
        return self.cur.lastrowid

    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {table_name}"
        params = ()
        if filters:
            conds = [f"{k} = %s" for k in filters.keys()]
            sql += " WHERE " + " AND ".join(conds)
            params = tuple(filters.values())
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        set_clause = ", ".join(f"{k} = %s" for k in new_values.keys())
        where_clause = " AND ".join(f"{k} = %s" for k in filters.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        params = tuple(new_values.values()) + tuple(filters.values())
        self.cur.execute(sql, params)
        self.conn.commit()
        return self.cur.rowcount

    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        where_clause = " AND ".join(f"{k} = %s" for k in filters.keys())
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        params = tuple(filters.values())
        self.cur.execute(sql, params)
        self.conn.commit()
        return self.cur.rowcount

    def close(self):
        self.cur.close()
        self.conn.close()
