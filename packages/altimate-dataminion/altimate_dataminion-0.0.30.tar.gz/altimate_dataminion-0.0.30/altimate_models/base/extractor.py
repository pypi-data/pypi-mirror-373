import logging
from typing import Optional, Text

from sqlalchemy import create_engine, inspect

from altimate_models.base.source import DataSource
from altimate_models.constants import TEST_SQL_QUERY


class SQLAlchemyExtractor:
    # TODO: currently allowing connection_str as well as datasource.
    # should get rid of raw strings passed around at some point: AL-639
    def __init__(
        self,
        connection_str: Optional[Text] = None,
        data_source: Optional[DataSource] = None,
    ):
        self.connection_str = connection_str
        self.data_source: DataSource = data_source
        self.engine = None
        self.connection = None

    def _initialize(self):
        if self.engine and self.connection:
            return

        try:
            self.engine = create_engine(self.connection_str)
            self.connection = self.engine.connect()
        except Exception:
            raise

    def _execute(self, sql: Text):
        if not self.connection:
            raise Exception("Connection has already been closed. Could not execute.")

        cs = self.connection.execute(sql)
        results = self._retrieve_results(cs)

        return results

    def _retrieve_results(self, cs):
        columns = [d.name for d in cs.cursor.description]
        rows = [dict(zip(columns, row)) for row in cs.fetchall()]

        return {
            "columns": columns,
            "rows": rows,
        }

    def _terminate(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

        if self.engine is not None:
            self.engine.dispose()
            self.engine = None

    def test(self):
        try:
            if self.data_source:
                with self.data_source.get_engine() as engine:
                    with engine.connect() as connection:
                        self.connection = connection
                        result = self._execute(TEST_SQL_QUERY)
                        rows = result["rows"]
                        columns = result["columns"]

                        return_result = (
                            len(rows) == 1 and rows[0][columns[0]] == 1
                        )  # TODO: Fix Indexing

                return return_result

            else:
                # Keeping this to support older connection_str method
                self._initialize()
                result = self._execute(TEST_SQL_QUERY)
                self._terminate()

                rows = result["rows"]
                columns = result["columns"]

                return len(rows) == 1 and rows[0][columns[0]] == 1  # TODO: Fix Indexing
        except Exception as e:
            logging.error(e)
            return False

    def foreign_keys(self, table_name: Text):
        self._initialize()

        inspector = inspect(self.engine)
        foreign_keys = inspector.get_foreign_keys(table_name)

        return foreign_keys

    def run(self, sql: Text):
        if self.data_source:
            with self.data_source.get_engine() as engine:
                with engine.connect() as connection:
                    self.connection = connection
                    results = self._execute(sql)
        else:
            self._initialize()
            results = self._execute(sql)
            self._terminate()

        return results
