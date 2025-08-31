

<p align="center">
	<img src="logo.png" alt="Mosaic ORM Logo" width="180"/>
</p>


# MosaicDB

Universal, framework-independent ORM for Python.

---

## Getting Started

```python
from pydantic import BaseModel
from mosaicdb import Mosaic
from mosaicdb.models import ModelMixin

class User(BaseModel, ModelMixin):
	id: int
	name: str
	age: int

db = Mosaic("sqlite:///test.db")
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
mosaicdb makemigrations users --db sqlite:///test.db --schema '{"id": "int", "name": "str"}'
mosaicdb migrate users --db sqlite:///test.db
mosaicdb create-table users --db sqlite:///test.db --schema '{"id": "int", "name": "str"}'
mosaicdb drop-table users --db sqlite:///test.db
mosaicdb inspect-schema users --db sqlite:///test.db
mosaicdb seed users --db sqlite:///test.db --data '{"id": 1, "name": "Alice"}'
mosaicdb raw-sql --db sqlite:///test.db --sql "SELECT * FROM users"
```

---

## Versioning & Changelog
- Current version: **v0.1.0-alpha**
- See `CHANGELOG.md` for updates.

---


## PyPI Installation

```bash
pip install mosaicdb
```

---

## License
MIT
