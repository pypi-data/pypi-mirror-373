from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session


def print_from_db():
    print("hello from DB")


class SQLAlchemyConnector:

    def __init__(self, db_url, schema):
        """
        Initialize the SQLAlchemyConnector with given DB URL and schema name.
        """
        self.db_url = db_url
        self.schema = schema
        self.engine = create_engine(self.db_url)
        self.session_factory = scoped_session(sessionmaker(bind=self.engine))

    def execute_and_fetch(self, query, params=None, many=False):
        """
        Execute a SELECT query and fetch results (one or many).
        """
        with self.session_factory() as session:
            result = session.execute(text(query), params=params)
            return result.fetchall() if many else result.fetchone()

    def execute_no_select(self, query, params=None):
        """
        Execute INSERT/UPDATE/DELETE query.
        """
        with self.session_factory() as session:
            session.execute(text(query), params=params)
            session.commit()

    def clear_table(self, table_name):
        """
        Truncate a table (with schema).
        """
        query = f"TRUNCATE TABLE {self.schema}.{table_name};"
        self.execute_no_select(query)

    def disable_triggers(self, object_name):
        """
        Disable all triggers on a table.
        """
        query = f"ALTER TABLE {self.schema}.{object_name} DISABLE TRIGGER ALL;"
        self.execute_no_select(query)

    def enable_triggers(self, object_name):
        """
        Enable all triggers on a table.
        """
        query = f"ALTER TABLE {self.schema}.{object_name} ENABLE TRIGGER ALL;"
        self.execute_no_select(query)
