from typing import Text, Dict

from altimate_models.duckdb.dialect import DuckDBSourceDialect
from altimate_models.s3.utils import gen_table_path
from altimate_models.shared_models import S3Resource


class JsonSourceDialect(DuckDBSourceDialect):

    DATA_QUERY = "data"
    METADATA_QUERY = "metadata"

    FORMAT_TO_TABLE_FUNCTION = {
        DATA_QUERY:  "read_json",
        METADATA_QUERY: "read_json",
    }

    @classmethod
    def create_table_path(cls, resource: S3Resource, query_type: Text) -> Text:
        return gen_table_path(resource.bucket, resource.path, resource.options, cls.FORMAT_TO_TABLE_FUNCTION[query_type])

    @classmethod
    def get_options(cls, options: Dict):
        if options is None:
            options = {}
        if not options.get('columns'):
            options['auto_detect'] = True
        return options

    @classmethod
    def schema_tables_query(
            cls,
            bucket: Text,
            path: Text,
            options: Dict
    ):
        options = cls.get_options(options)
        options["json_format"] = "array_of_records"
        return f" DESCRIBE SELECT * FROM " \
               f"{gen_table_path(bucket, path, options, cls.FORMAT_TO_TABLE_FUNCTION[cls.METADATA_QUERY])}"

    @classmethod
    def _base_query_sample(
            cls,
            select_sql: Text,
            bucket: Text,
            path: Text,
            options: Dict,
            filters: Text = None
    ):
        options = cls.get_options(options)
        table = gen_table_path(bucket, path, options, cls.FORMAT_TO_TABLE_FUNCTION[cls.DATA_QUERY])
        sql = """
            SELECT 
                {select_sql}
            FROM {table}
        """.format(
            select_sql=select_sql,
            table=table,
        )
        if filters:
            sql += f" WHERE {filters}"
        return sql

    @classmethod
    def _table_sql(
            self,
            bucket: Text,
            path: Text,
            options: Dict,
            filters=None
    ):
        options = self.get_options(options)
        table = gen_table_path(bucket, path, options, self.FORMAT_TO_TABLE_FUNCTION[self.DATA_QUERY])
        if filters:
            table += " WHERE " + filters
        return table
