import json
import pytest

from .commands.schema import PGDatabase, PGDatabaseEncoder


@pytest.mark.skip(reason="Requires PostgreSQL database setup")
def test_dump_schema_as_json(postgresql_external):
    cur = postgresql_external.cursor()
    cur.execute("CREATE TABLE test(a int primary key, b int)")
    cur.execute("CREATE INDEX test_ind ON test (b)")
    postgresql_external.commit()
    cur.close()
    db = PGDatabase(postgresql_external)
    db.load()
    json.dumps(db, cls=PGDatabaseEncoder)
