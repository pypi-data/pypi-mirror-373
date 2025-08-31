"""pytest tests for mosaic SQLite driver - MVP single table CRUD."""

import os
import tempfile
from mosaic import Mosaic
from mosaic.exceptions import TableNotFoundError, MosaicError

def test_crud_lifecycle():
    # use a temporary file database
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        db = Mosaic(f"sqlite://{path}")
        db.create_table("people", {"id": "int", "name": "str", "age": "int"})
        r1 = db.insert("people", {"name": "Test", "age": 42})
        assert isinstance(r1, int) and r1 > 0

        rows = db.find("people")
        assert len(rows) == 1
        assert rows[0]["name"] == "Test"
        assert rows[0]["age"] == 42

        # update
        c = db.update("people", {"id": r1}, {"age": 43})
        assert c == 1
        after = db.find("people", {"id": r1})
        assert after[0]["age"] == 43

        # delete
        d = db.delete("people", {"id": r1})
        assert d == 1
        final = db.find("people")
        assert final == []

        db.close()
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

def test_table_not_found():
    db = Mosaic("sqlite:///:memory:")
    try:
        try:
            db.find("no_such_table")
        except TableNotFoundError:
            pass
        else:
            raise AssertionError("expected TableNotFoundError")
    finally:
        db.close()

def test_invalid_schema():
    db = Mosaic("sqlite:///:memory:")
    try:
        # invalid schema (not a dict)
        try:
            db.create_table("t", None)
        except MosaicError:
            pass
        else:
            raise AssertionError("expected MosaicError for invalid schema")
    finally:
        db.close()
