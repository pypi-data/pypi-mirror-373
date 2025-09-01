"""PostgreSQL driver for akron."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional, List, Tuple
from ..core.base import BaseDriver
from ..exceptions import AkronError, TableNotFoundError

class PostgresDriver(BaseDriver):
    def __init__(self, db_url: str):
        """db_url format: postgres://user:password@host:port/dbname"""
        import re
        pattern = r"postgres://(.*?):(.*?)@(.*?):(.*?)/(.*?)$"
        match = re.match(pattern, db_url)
        if not match:
            raise AkronError("Invalid Postgres URL format")
        user, password, host, port, database = match.groups()
        self.conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=int(port),
            dbname=database
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        cols = []
        fks = []
        for col, dtype in schema.items():
            # Foreign key syntax: 'type->table.column'
            if isinstance(dtype, str) and "->" in dtype:
                base_type, fk = dtype.split("->", 1)
                sql_type = "INTEGER" if base_type.strip() == "int" else "VARCHAR(255)" if base_type.strip() == "str" else base_type.strip().upper()
                ref_table, ref_col = fk.strip().split(".")
                cols.append(f"{col} {sql_type}")
                fks.append(f"FOREIGN KEY({col}) REFERENCES {ref_table}({ref_col})")
            else:
                sql_type = "INTEGER" if dtype == "int" else "VARCHAR(255)" if dtype == "str" else dtype.upper()
                if col == "id" and sql_type == "INTEGER":
                    cols.append(f"{col} {sql_type} PRIMARY KEY GENERATED ALWAYS AS IDENTITY")
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
        sql = f"INSERT INTO {table_name} ({cols_sql}) VALUES ({placeholders}) RETURNING id"
        params = tuple(data.values())
        self.cur.execute(sql, params)
        self.conn.commit()
        return self.cur.fetchone()["id"]

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
