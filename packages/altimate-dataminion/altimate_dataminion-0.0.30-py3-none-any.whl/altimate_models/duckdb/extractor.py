import logging
import sys
from typing import Text

from altimate_models.constants import TEST_SQL_QUERY

try:
    import duckdb
except ImportError:
    pass

from altimate_profiler.exceptions import (
    INVALID_UNICODE_IN_CSV,
    AltimateInvalidCharactersInCSVException,
    AltimateInvalidInputException,
)


class DuckDBExtractor:
    def __init__(
        self,
        connection_str: Text,
    ):
        self.connection_str = connection_str
        self.engine = None

    def _initialize(self):
        raise NotImplementedError(
            "Cannot use DuckDBExtractor directly. Please use an implementation like S3Extractor."
        )

    def _create_engine(self, connection_str: Text):
        if not "duckdb" in sys.modules:
            raise ImportError("Could not import duckdb. Please install duckdb.")
        engine = duckdb.connect(database=":memory:", read_only=False)
        engine.execute(connection_str)
        return engine

    def _execute(self, sql: Text):
        if not self.engine:
            raise Exception("Connection has already been closed. Could not execute.")
        try:
            cs = self.engine.sql(sql)
            results = self._retrieve_results(cs)
        except duckdb.InvalidInputException as e:
            if INVALID_UNICODE_IN_CSV in str(e):
                raise AltimateInvalidCharactersInCSVException(
                    "CSV file contains invalid unicode characters. This is not supported currently."
                    "We only support UTF-8 encoded / ISO-8849 CSV files."
                )
            else:
                raise AltimateInvalidInputException(
                    f"The column configuration might be incorrect." f" Exception: {e}"
                )

        return results

    def _retrieve_results(self, cs):
        data_dict = cs.fetchdf().to_dict("split")
        columns = data_dict["columns"]
        rows = [dict(zip(columns, row)) for row in data_dict["data"]]

        return {
            "columns": columns,
            "rows": rows,
        }

    def _terminate(self):
        if self.engine:
            self.engine.close()
            self.engine = None

    def test(self):
        try:
            self._initialize()
            result = self._execute(TEST_SQL_QUERY)
            self._terminate()

            rows = result["rows"]
            columns = result["columns"]

            return len(rows) == 1 and rows[0][columns[0]] == 1  # TODO: Fix Indexing
        except Exception as e:
            logging.error(e)
            return False

    def run(self, sql: Text):
        self._initialize()

        results = self._execute(sql)

        self._terminate()

        return results
