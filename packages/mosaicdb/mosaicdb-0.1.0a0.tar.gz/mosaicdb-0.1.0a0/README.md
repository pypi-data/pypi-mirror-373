
# Mosaic ORM

Universal, framework-independent ORM for Python.

---

## Getting Started

```python
from pydantic import BaseModel
from mosaic import Mosaic
from mosaic.models import ModelMixin

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
python mosaic/cli.py makemigrations users --db sqlite:///test.db --schema '{"id": "int", "name": "str"}'
python mosaic/cli.py migrate users --db sqlite:///test.db
python mosaic/cli.py create-table users --db sqlite:///test.db --schema '{"id": "int", "name": "str"}'
python mosaic/cli.py drop-table users --db sqlite:///test.db
python mosaic/cli.py inspect-schema users --db sqlite:///test.db
python mosaic/cli.py seed users --db sqlite:///test.db --data '{"id": 1, "name": "Alice"}'
python mosaic/cli.py raw-sql --db sqlite:///test.db --sql "SELECT * FROM users"
```

---

## Versioning & Changelog
- Current version: **v0.1.0-alpha**
- See `CHANGELOG.md` for updates.

---

## PyPI Installation

```bash
pip install mosaic-orm
```

---

## License
MIT
