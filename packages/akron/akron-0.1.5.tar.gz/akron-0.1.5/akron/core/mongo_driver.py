"""MongoDB driver for akron."""

from pymongo import MongoClient
from typing import Dict, Any, Optional, List
from .base import BaseDriver
from ..exceptions import AkronError

class MongoDriver(BaseDriver):
    def __init__(self, db_url: str):
        """db_url format: mongodb://host:port/dbname"""
        # Example: mongodb://localhost:27017/akron_test
        import re
        pattern = r"mongodb://(.*?):(\d+)/(.*?)$"
        match = re.match(pattern, db_url)
        if not match:
            raise AkronError("Invalid MongoDB URL format")
        host, port, database = match.groups()
        self.client = MongoClient(host, int(port))
        self.db = self.client[database]

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        # MongoDB is schemaless; just create collection if not exists
        self.db.create_collection(table_name)

    def insert(self, table_name: str, data: Dict[str, Any]) -> Any:
        result = self.db[table_name].insert_one(data)
        return result.inserted_id

    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if filters is None:
            filters = {}
        return list(self.db[table_name].find(filters))

    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        result = self.db[table_name].update_many(filters, {"$set": new_values})
        return result.modified_count

    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        result = self.db[table_name].delete_many(filters)
        return result.deleted_count

    def close(self):
        self.client.close()
