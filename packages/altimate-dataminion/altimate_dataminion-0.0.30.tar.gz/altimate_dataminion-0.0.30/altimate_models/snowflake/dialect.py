from typing import List, Text

from altimate_models.base.dialect import SQLAlchemySourceDialect


class SnowflakeSourceDialect(SQLAlchemySourceDialect):
    @classmethod
    def _max_execution_time(cls, params) -> Text:
        return (
            "SELECT COALESCE(MAX(EXECUTION_TIME/1000), 0) FROM snowflake.account_usage.query_history"
            " WHERE END_TIME >= DATEADD('hour', -{hours}, CURRENT_TIMESTAMP())".format(
                hours=params.get("hours", 1)
            )
        )

    @classmethod
    def _min_bytes_spilled_to_local_storage(cls, params) -> Text:
        return (
            "SELECT  COALESCE(MIN(BYTES_SPILLED_TO_LOCAL_STORAGE), 0) FROM snowflake.account_usage.query_history"
            " WHERE END_TIME >= DATEADD('hour', -{hours}, CURRENT_TIMESTAMP())".format(
                hours=params.get("hours", 1)
            )
        )

    @classmethod
    def _cardinality(cls):
        return "COUNT(DISTINCT md5({column}))"

    @classmethod
    def _null_percentage(cls):
        return "SUM(IFF({column} IS NULL, 1 , 0))/COALESCE(COUNT(*), 1) *100"

    @classmethod
    def _max_credits_consumed_by_warehouse(cls, params) -> Text:
        return (
            "SELECT COALESCE(MAX(CREDITS_USED), 0) FROM snowflake.account_usage.warehouse_metering_history"
            " WHERE END_TIME >= DATEADD('hour', -{hours}, CURRENT_TIMESTAMP())".format(
                hours=params.get("hours", 1)
            )
        )

    @classmethod
    def _duplicate_count(cls, table, params):
        return "SELECT COALESCE(COUNT(c), 0) AS duplicates FROM (SELECT HASH(ARRAY_TO_STRING(ARRAY_CONSTRUCT({columns}), ',')) AS hash_value, COUNT(*) AS c FROM {table} GROUP BY hash_value HAVING COUNT(*) > 1) AS t".format(
            columns=",".join(params["columns"]), table=table
        )

    @classmethod
    def _null_count(cls):
        return "SUM(IFF({column} IS NULL, 1 , 0))"

    @classmethod
    def _regex_match_percentage(cls):
        return "SUM(IFF({column}::TEXT REGEXP '{pattern}', 1 , 0)) / COALESCE(COUNT(*), 1) * 100"

    @classmethod
    def _like_percentage(cls):
        return "SUM(IFF({column}:: TEXT  LIKE '{pattern}', 1 , 0)) / COALESCE(COUNT(*), 1) * 100"

    @classmethod
    def _null_count_table(cls, table, params):
        condition = " AND ".join([f"{column} IS NULL" for column in params["columns"]])
        return f"SELECT SUM(IFF({condition}, 1, 0))  FROM {table}".format(
            table=table, condition=condition
        )

    @classmethod
    def _allowed_values(cls):
        return "SUM(IFF({column} NOT IN {values}, 1 , 0))"

    @classmethod
    def _max_credits_consumed_by_query(cls, params) -> Text:
        sql = """
            WITH
                warehouse_sizes AS (
                    SELECT 'X-Small' AS warehouse_size, 1 AS credits_per_hour UNION ALL
                    SELECT 'Small' AS warehouse_size, 2 AS credits_per_hour UNION ALL
                    SELECT 'Medium'  AS warehouse_size, 4 AS credits_per_hour UNION ALL
                    SELECT 'Large' AS warehouse_size, 8 AS credits_per_hour UNION ALL
                    SELECT 'X-Large' AS warehouse_size, 16 AS credits_per_hour UNION ALL
                    SELECT '2X-Large' AS warehouse_size, 32 AS credits_per_hour UNION ALL
                    SELECT '3X-Large' AS warehouse_size, 64 AS credits_per_hour UNION ALL
                    SELECT '4X-Large' AS warehouse_size, 128 AS credits_per_hour
                )
                SELECT
                    COALESCE(MAX(qh.execution_time/(1000*60*60)*wh.credits_per_hour) , 0) AS query_cost
                FROM snowflake.account_usage.query_history AS qh
                INNER JOIN warehouse_sizes AS wh
                    ON qh.warehouse_size=wh.warehouse_size
                WHERE
                    END_TIME >= DATEADD('hour', -{hours}, CURRENT_TIMESTAMP())
        
        """
        return sql.format(hours=params.get("hours", 1))

    @classmethod
    def _numeric_mode(cls):
        return "MODE({column})"

    @classmethod
    def _numeric_median(cls):
        return "MEDIAN({column})"

    @classmethod
    def _percentage_selects(cls):
        return "SUM(IFF(TO_VARCHAR({column}) = 'SELECT', 1, 0)) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _percentile(cls):
        return "PERCENTILE_CONT({value}) WITHIN GROUP (ORDER BY {column})"

    @classmethod
    def _conditional_count(cls):
        return "SUM(IFF({condition}, 1, 0))"

    @classmethod
    def _conditional_percentage(cls):
        return "SUM(IFF({condition}, 1, 0)) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _conditional_max(cls):
        return "MAX(IFF({condition}, {column}, NULL))"

    @classmethod
    def _conditional_min(cls):
        return "MIN(IFF({condition}, {column}, NULL))"

    @classmethod
    def _conditional_mean(cls):
        return "AVG(IFF({condition}, {column}, NULL))"

    @classmethod
    def _percentage_inserts(cls):
        return "SUM(IFF(TO_VARCHAR({column}) = 'INSERT', 1, 0)) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _percentage_warehouse_size_x_small(cls):
        return "SUM(IFF(TO_VARCHAR({column}) = 'X-Small', 1, 0)) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _percentage_failures(cls):
        return "SUM(IFF(TO_VARCHAR({column}) LIKE '%FAIL%', 1, 0)) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _percentage_warehouse_is_xsmall(cls):
        return (
            "SUM(IFF( (TO_VARCHAR({column}) = 'SELECT') AND (WAREHOUSE_SIZE = 'X-Small'), 1, 0)) * 100"
            "/ SUM(IFF( (TO_VARCHAR({column}) = 'SELECT') AND (WAREHOUSE_SIZE IS NOT NULL), 1, 0))"
        )

    @classmethod
    def _avg_rows_inserted_or_updated(cls):
        return (
            "SUM(IFF( QUERY_TYPE = 'INSERT', "
            "ROWS_UPDATED + ROWS_INSERTED, 0)) / SUM(IFF( QUERY_TYPE = 'INSERT', 1, 0)) "
        )

    @classmethod
    def _average_non_negative(cls):
        """
        The execution time for the query_history column is negative for
        queries to the query_history table.
        """
        return "AVG(IFF({column} >= 0 , {column}, 0))"

    @classmethod
    def _avg_select_query_time(cls):
        return "AVG(IFF( QUERY_TYPE = 'SELECT', TOTAL_ELAPSED_TIME, 0))"

    @classmethod
    def _max_non_negative(cls):
        return "MAX(IFF({column} >= 0 , {column}, 0))"

    @classmethod
    def _min_non_negative(cls):
        return "MIN(IFF({column} >= 0 , {column}, 0))"

    @classmethod
    def _text_int_rate(cls):
        return (
            "SUM(IFF(REGEXP_COUNT(TO_VARCHAR({column}), '^([-+]?[0-9]+)$', 1, 'i') != 0, 1,"
            " 0)) / COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _text_number_rate(cls):
        return (
            "SUM(IFF(REGEXP_COUNT(TO_VARCHAR({column}),"
            " '^([-+]?[0-9]*[.]?[0-9]+([eE][-+]?[0-9]+)?)$', 1, 'i') != 0, 1, 0)) /"
            " COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _text_uuid_rate(cls):
        return (
            "SUM(IFF(REGEXP_COUNT(TO_VARCHAR({column}),"
            " '^([0-9a-fA-F]{{8}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{12}})$',"
            " 1, 'i') != 0, 1, 0)) / COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _text_all_spaces_rate(cls):
        return (
            "SUM(IFF(REGEXP_COUNT(TO_VARCHAR({column}), '^(\\\\s+)$', 1, 'i') != 0, 1, 0)) /"
            " COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _text_null_keyword_rate(cls):
        return (
            "SUM(IFF(UPPER({column}) IN ('NULL', 'NONE', 'NIL', 'NOTHING'), 1, 0)) /"
            " COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _zero_rate(cls):
        return (
            "SUM(IFF(UPPER({column}) IN ('NULL', 'NONE', 'NIL', 'NOTHING'), 1, 0)) /"
            " COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _negative_rate(cls):
        return "SUM(IFF({column} < 0, 1, 0)) / COALESCE(COUNT(*), 1)"

    @classmethod
    def _dates_in_future_percentage(cls):
        return "SUM(IFF({column} > CURRENT_TIMESTAMP(), 1, 0)) / COALESCE(COUNT(*), 1) * 100"

    @classmethod
    def _completeness(cls):
        return "COUNT({column}) / CAST(COUNT(*) AS NUMERIC)"

    @classmethod
    def _invalid_email_rate(cls):
        return (
            "SUM(IFF(REGEXP_COUNT(TO_VARCHAR({column}),"
            " '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9\\\-.]+$',"
            " 1, 'i') != 0, 0, 1)) / COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _freshness(cls, table, params):
        column = params.get("column")
        time_unit = params.get("timeUnit")
        return "select min(datediff({time_unit}, {column}, current_timestamp())) from {table}".format(
            table=table, column=column, time_unit=time_unit
        )

    @classmethod
    def schema_tables_query(
        cls,
        database_name: Text,
        schema_name: Text,
        table_name: Text = None,
        filters: Text = None,
        schemas_to_exclude: List[Text] = ["information_schema"],
    ) -> Text:
        excluded_schemas_string = ", ".join(
            ["'{}'".format(schema) for schema in schemas_to_exclude]
        )
        return """
            SELECT 
              TABLE_CATALOG, 
              TABLE_SCHEMA,
              TABLE_NAME, 
              TABLE_OWNER, 
              TABLE_TYPE, 
              IS_TRANSIENT, 
              RETENTION_TIME, 
              AUTO_CLUSTERING_ON, 
              COMMENT 
            FROM {database_name}.information_schema.tables 
            WHERE 
              table_schema NOT IN ({excluded_schemas_string}) 
              AND TABLE_TYPE NOT IN ('VIEW', 'EXTERNAL TABLE') 
              AND LOWER( TABLE_SCHEMA ) = LOWER('{schema_name}')
            ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME;
        """.format(
            database_name=database_name,
            schema_name=schema_name,
            excluded_schemas_string=excluded_schemas_string,
        )

    @classmethod
    def schema_columns_query(
        cls,
        database_name: Text,
        schema_name: Text,
        table_name: Text = None,
        filters: Text = None,
        schemas_to_exclude: List[Text] = ["information_schema"],
        use_account_usage: bool = False,
    ) -> Text:
        
        if use_account_usage:
            # Build schema filter for subqueries
            excluded_schemas_string = ", ".join(
                ["'{}'".format(schema.upper()) for schema in schemas_to_exclude]
            )
            
            if schema_name:
                schema_filter = f"AND LOWER(table_schema) = LOWER('{schema_name}')"
            else:
                schema_filter = f"AND UPPER(table_schema) NOT IN ({excluded_schemas_string})"
            
            sql = """
                SELECT
                    lower(c.table_name) AS NAME,
                    lower(c.column_name) AS COL_NAME,
                    lower(c.data_type) AS COL_TYPE,
                    c.comment AS COL_DESCRIPTION,
                    lower(c.ordinal_position) AS COL_SORT_ORDER,
                    lower(c.table_catalog) AS DATABASE,
                    lower(c.table_schema) AS SCHEMA,
                    t.comment AS DESCRIPTION,
                    decode(lower(t.table_type), 'view', 'true', 'false') AS IS_VIEW
                FROM
                    (SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.COLUMNS 
                    WHERE LOWER(table_catalog) = LOWER('{database_name}') 
                    AND deleted IS NULL
                    {schema_filter}) AS c
                LEFT JOIN
                    (SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES 
                    WHERE LOWER(table_catalog) = LOWER('{database_name}') 
                    AND deleted IS NULL
                    {schema_filter}) t
                        ON c.TABLE_NAME = t.TABLE_NAME
                        AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
                        AND c.TABLE_CATALOG = t.TABLE_CATALOG
            """.format(
                database_name=database_name, 
                schema_filter=schema_filter
            )

            # Add additional filters after the main query for account usage
            where_conditions = []
            
            if table_name:
                where_conditions.append(f"LOWER(NAME) = LOWER('{table_name}')")

            if filters:
                where_conditions.append(filters)

            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
                
        else:
            # Original INFORMATION_SCHEMA approach
            sql = """
                SELECT
                    lower(c.table_name) AS NAME,
                    lower(c.column_name) AS COL_NAME,
                    lower(c.data_type) AS COL_TYPE,
                    c.comment AS COL_DESCRIPTION,
                    lower(c.ordinal_position) AS COL_SORT_ORDER,
                    lower(c.table_catalog) AS DATABASE,
                    lower(c.table_schema) AS SCHEMA,
                    t.comment AS DESCRIPTION,
                    decode(lower(t.table_type), 'view', 'true', 'false') AS IS_VIEW
                FROM
                    {database_name}.INFORMATION_SCHEMA.COLUMNS AS c
                LEFT JOIN
                    {database_name}.INFORMATION_SCHEMA.TABLES t
                        ON c.TABLE_NAME = t.TABLE_NAME
                        AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
                WHERE LOWER( c.table_catalog ) = LOWER('{database_name}')
            """.format(
                database_name=database_name, schema_name=schema_name
            )

            excluded_schemas_string = ", ".join(
                ["'{}'".format(schema) for schema in schemas_to_exclude]
            )
            
            if schema_name:
                sql += f" AND LOWER( c.table_schema ) = LOWER('{schema_name}')"
            else:
                sql += f" AND LOWER( c.table_schema ) NOT IN ({excluded_schemas_string})"

            if table_name:
                sql += f" AND LOWER(c.table_name) = LOWER('{table_name}')"

            if filters:
                sql += f" AND {filters}"

        return sql

    @classmethod
    def access_logs_query(cls):
        return """
            SELECT 
                "QUERY_TEXT", 
                "DATABASE_NAME", 
                "SCHEMA_NAME", 
                "QUERY_TYPE", 
                "USER_NAME", 
                "ROLE_NAME", 
                "EXECUTION_STATUS", 
                "START_TIME", 
                "END_TIME", 
                "TOTAL_ELAPSED_TIME", 
                "BYTES_SCANNED", 
                "ROWS_PRODUCED", 
                "SESSION_ID", 
                "QUERY_ID", 
                "QUERY_TAG", 
                "WAREHOUSE_NAME", 
                "ROWS_INSERTED", 
                "ROWS_UPDATED", 
                "ROWS_DELETED", 
                "ROWS_UNLOADED" 
            FROM snowflake.account_usage.query_history 
            WHERE 
                start_time BETWEEN to_timestamp_ltz('2021-01-01 00:00:00.000000+00:00') AND to_timestamp_ltz('2021-01-01 01:00:00.000000+00:00') 
                AND QUERY_TYPE NOT IN ('DESCRIBE', 'SHOW') 
                AND (DATABASE_NAME IS NULL OR DATABASE_NAME NOT IN ('UTIL_DB', 'SNOWFLAKE')) 
                AND ERROR_CODE is NULL 
            ORDER BY start_time DESC;
        """

    @classmethod
    def copy_and_load_logs_query(cls):
        return """
            SELECT 
                "FILE_NAME", 
                "STAGE_LOCATION", 
                "LAST_LOAD_TIME", 
                "ROW_COUNT", 
                "FILE_SIZE", 
                "ERROR_COUNT", 
                "STATUS", 
                "TABLE_CATALOG_NAME", 
                "TABLE_SCHEMA_NAME", 
                "TABLE_NAME", 
                "PIPE_CATALOG_NAME", 
                "PIPE_SCHEMA_NAME", 
                "PIPE_NAME", 
                "PIPE_RECEIVED_TIME" 
            FROM snowflake.account_usage.copy_history 
            WHERE 
                LAST_LOAD_TIME between to_timestamp_ltz('2021-01-01 00:00:00.000000+00:00') AND to_timestamp_ltz('2021-01-01 01:00:00.000000+00:00')
                AND STATUS != 'load failed' 
            ORDER BY LAST_LOAD_TIME DESC;
        """
