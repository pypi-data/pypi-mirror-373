

<p align="center">
	<img src="https://res.cloudinary.com/dclp2h92a/image/upload/v1756577773/ChatGPT_Image_Aug_30_2025_11_01_26_PM_i6o5k7.png" alt="Akron ORM Logo" width="180"/>
</p>



# Akron

Universal, framework-independent ORM for Python.

---

## Getting Started

```python
from pydantic import BaseModel

from akron import Akron
from akron.models import ModelMixin

class User(BaseModel, ModelMixin):
	id: int
	name: str
	age: int

db = Akron("sqlite:///test.db")
User.create_table(db)
User.insert(db, User(id=1, name="Alice", age=30))
users = User.find(db)
print(users)
```

---

## Features Table
| Feature                | Supported |
|------------------------|-----------|
| Simple Syntax          | ✅        |
| Multi-DB Support       | ✅        |
| Multi-Table/FK         | ✅        |
| Auto Migrations        | ✅        |
| CLI                    | ✅        |
| Typesafe Models        | ✅        |
| NoSQL (MongoDB)        | ✅        |
| Error Handling         | ✅        |
| Test Coverage          | ✅        |

---

## Database Support Matrix
| Database    | CRUD | FKs | Migrations | CLI | Typesafe Models |
|-------------|------|-----|------------|-----|-----------------|
| SQLite      | ✅   | ✅  | ✅         | ✅  | ✅              |
| MySQL       | ✅   | ✅  | ✅         | ✅  | ✅              |
| PostgreSQL  | ✅   | ✅  | ✅         | ✅  | ✅              |
| MongoDB     | ✅   | ❌  | Schemaless | ✅  | ✅              |

---

## CLI Command Examples

```bash
akron makemigrations users --db sqlite:///test.db --schema '{"id": "int", "name": "str"}'
akron migrate users --db sqlite:///test.db
akron create-table users --db sqlite:///test.db --schema '{"id": "int", "name": "str"}'
akron drop-table users --db sqlite:///test.db
akron inspect-schema users --db sqlite:///test.db
akron seed users --db sqlite:///test.db --data '{"id": 1, "name": "Alice"}'
akron raw-sql --db sqlite:///test.db --sql "SELECT * FROM users"
```

---

## Versioning & Changelog
- Current version: **v0.1.1**
- See `CHANGELOG.md` for updates.

---


## PyPI Installation

```bash
pip install akron
```

---

## License
[MIT](LICENSE)
