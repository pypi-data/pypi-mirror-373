"""Typesafe model support for Akron using Pydantic."""
from pydantic import BaseModel, Field
from typing import Type, Dict, Any

SQL_TYPE_MAP = {
    int: "int",
    str: "str",
    float: "float",
    bool: "bool"
}

def model_to_schema(model_cls: Type[BaseModel]) -> Dict[str, str]:
    schema = {}
    for name, field in model_cls.model_fields.items():
        py_type = field.annotation
        sql_type = SQL_TYPE_MAP.get(py_type, "str")
        schema[name] = sql_type
    return schema

class ModelMixin:
    @classmethod
    def create_table(cls, db):
        schema = model_to_schema(cls)
        db.create_table(cls.__name__.lower(), schema)

    @classmethod
    def insert(cls, db, obj):
        data = obj.model_dump()
        return db.insert(cls.__name__.lower(), data)

    @classmethod
    def find(cls, db, filters=None):
        results = db.find(cls.__name__.lower(), filters)
        return [cls(**r) for r in results]

    @classmethod
    def update(cls, db, filters, new_values):
        return db.update(cls.__name__.lower(), filters, new_values)

    @classmethod
    def delete(cls, db, filters):
        return db.delete(cls.__name__.lower(), filters)
