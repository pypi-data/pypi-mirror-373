import json

SCHEMA_QUERY = """
select
    oid,
    nspname
from pg_catalog.pg_namespace
where
    nspname not in ('pg_catalog', 'information_schema') and
    nspname not like 'pg_toast%' and
    nspname not like 'pg_temp%'
"""

TABLE_QUERY = """
select
    oid,
    relname,
    relnamespace,
    reltablespace,
    relpersistence
from pg_class pgc
where
    relkind in ('r','p') and
    relnamespace not in (
        select oid
        from pg_namespace
        where
            nspname in ('pg_catalog', 'information_schema') or
            nspname like 'pg_toast%'
    )
"""

COLUMN_QUERY = """
select
    pn.nspname ,
    pgc.relname,
    a.attname,
    a.attnum,
    pg_catalog.format_type(t.oid, a.atttypmod) as atttypname,
    a.attnotnull,
    coalesce(
    case
        when a.attgenerated = ''::"char" then pg_get_expr(ad.adbin,
        ad.adrelid)
        else ''
    end,'') as column_default
from
    pg_catalog.pg_attribute a
left join pg_catalog.pg_type t on
    a.atttypid = t.oid
left join pg_catalog.pg_class pgc on
    a.attrelid = pgc.oid
left join pg_catalog.pg_namespace pn on
    pgc.relnamespace = pn.oid
left join pg_attrdef ad on
    a.attrelid = ad.adrelid
    and a.attnum = ad.adnum
where
    pn.nspname not in ('pg_catalog', 'pg_toast', 'information_schema')
    and attnum > 0
    and pgc.relkind in ('r', 'f', 'p')
    and not a.attisdropped
"""

INDEX_QUERY = """
select
    i_index.oid index_oid,
    i_index.relname index_name,
    i_index.relnamespace schema_oid,
    i_index.reltablespace index_tablespace,
    i_table.oid table_oid,
    pg_index.indisunique is_unique,
    pg_index.indisprimary is_primary_key,
    pg_catalog.pg_get_indexdef(pg_index.indexrelid) as indexdef
from pg_class i_index
left join pg_index on pg_index.indexrelid = i_index.oid
left join pg_class i_table on pg_index.indrelid = i_table.oid
left join pg_catalog.pg_constraint c
    on(pg_index.indrelid = c.conrelid AND pg_index.indexrelid = c.conindid)
where
    i_index.relkind = 'i' and
    c.conrelid is null and
    i_index.relnamespace not in (
        select oid
        from pg_namespace
        where
            nspname in ('pg_catalog', 'information_schema') or
            nspname like 'pg_toast%'
    )
"""


class PGObject:
    def to_json(self):
        raise Exception("should be overridden by concrete class")


class PGIndex(PGObject):
    def __init__(self, oid, name):
        self.oid = oid
        self.name = name
        self.tablespace = None
        self.is_unique = None
        self.is_primary = None
        self.definition = None
        self.table_name = None
        self.schema_name = None

    def to_json(self):
        return {
            "oid": self.oid,
            "schema": self.schema_name,
            "name": self.name,
            "tablespace": self.tablespace,
            "tableName": self.table_name,
            "isUnique": self.is_unique,
            "isPrimary": self.is_primary,
            "definition": self.definition,
        }


class PGColumn(PGObject):
    def __init__(self, ordinal_pos, name):
        self.ordinalpos = ordinal_pos
        self.name = name
        self.data_type = None
        self.not_null = None
        self.default_value = None
        self.precision = None
        self.char_max_length = None

    def to_json(self):
        return {
            "name": self.name,
            "ordinalPosition": self.ordinalpos,
            "notNull": self.not_null,
            "dataType": self.data_type,
            "defaultValue": self.default_value,
        }


class PGTable(PGObject):
    def __init__(self, oid, name):
        self.oid = oid
        self.name = name
        self.schema_name = None
        self.tablespace = None
        self.is_persistent = None
        self.inherited_table_oids = list()
        self.name_to_columns = dict()

    def to_json(self):
        return {
            "oid": self.oid,
            "schema": self.schema_name,
            "name": self.name,
            "persistent": self.is_persistent,
            "inheritedTableOids": self.inherited_table_oids,
            "tablespace": self.tablespace,
            "columns": self.name_to_columns,
        }


class PGSchema(PGObject):
    def __init__(self, oid, name):
        self.oid = oid
        self.name = name
        self.name_to_table = dict()
        self.name_to_constraint = dict()
        self.name_to_index = dict()

    def to_json(self):
        return {
            "name": self.name,
            "tables": self.name_to_table,
            "indexes": self.name_to_index,
            "constraints": self.name_to_constraint,
        }


class PGDatabase(PGObject):
    def __init__(self, conn):
        self.conn = conn
        self.name = conn.info.dbname
        self.name_to_schema = dict()
        self.schema_oid_to_name = dict()
        self.table_oid_to_table = dict()

    def to_json(self):
        return {
            "name": self.name,
            "schemas": self.name_to_schema,
        }

    def get_schemas(self):
        cursor = self.conn.cursor()
        cursor.execute(SCHEMA_QUERY)

        for result in cursor.fetchall():
            self.name_to_schema[result[1]] = PGSchema(oid=result[0], name=result[1])
            self.schema_oid_to_name[result[0]] = result[1]

        self.get_tables()
        self.get_columns()
        self.get_indexes()

    def get_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(TABLE_QUERY)

        for result in cursor.fetchall():
            schema_name = self.schema_oid_to_name[result[2]]
            schema = self.name_to_schema[schema_name]

            table = PGTable(oid=result[0], name=result[1])
            table.tablespace = result[3]
            table.is_persistent = "p" if result[4] else "u"
            table.schema_name = schema_name

            schema.name_to_table[table.name] = table
            self.table_oid_to_table[table.oid] = table

    def get_columns(self):
        cursor = self.conn.cursor()
        cursor.execute(COLUMN_QUERY)

        for result in cursor.fetchall():
            schema_name = result[0]
            table_name = result[1]

            column = PGColumn(ordinal_pos=result[3], name=result[2])
            column.data_type = result[4]
            column.not_null = result[5]
            column.default_value = result[6]

            schema = self.name_to_schema[schema_name]
            table = schema.name_to_table[table_name]
            table.name_to_columns[column.name] = column

    def get_indexes(self):
        cursor = self.conn.cursor()
        cursor.execute(INDEX_QUERY)

        for result in cursor.fetchall():
            schema_oid = result[2]
            table_oid = result[4]

            index = PGIndex(oid=result[0], name=result[1])
            index.tablespace = result[3]
            index.is_unique = result[5]
            index.is_primary = result[6]
            index.definition = result[7]

            table = self.table_oid_to_table[table_oid]
            index.table_name = table.name

            schema_name = self.schema_oid_to_name[schema_oid]
            index.schema_name = schema_name
            schema = self.name_to_schema[schema_name]
            schema.name_to_index[index.name] = index

    def load(self):
        # TODO: get extensions
        self.get_schemas()


class PGDatabaseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PGObject):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)
