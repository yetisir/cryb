import sqlalchemy as sql
from sqlalchemy.ext import declarative
from sqlalchemy.orm import sessionmaker

from ... import connections


class Database:

    engine = sql.create_engine(connections.postgresql())
    session = sessionmaker(bind=engine)()
    Table = declarative.declarative_base()
    Table.metadata.bind = engine

    @classmethod
    def create_all(cls):
        cls.Table.metadata.create_all()

    @classmethod
    def schema_metadata(cls, schema_cls):
        class Meta:
            model = schema_cls
            load_instance = True
            sqla_session = cls.session
            include_fk = True
            include_relationships = True
        return Meta
