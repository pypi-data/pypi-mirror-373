from uuid import uuid4

from altimate_profiler.transformer.base import Transformer


class SchemaTransformer(Transformer):
    """
    Transforms the schema collected by the SchemaCollectorJob into JSON Output
    """

    @classmethod
    def _original_schema(cls):
        return {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "rows": {"type": "array", "items": {"type": "object"}, "minItems": 1},
                "columns": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["rows", "columns"],
        }

    @classmethod
    def _normalized_schema(cls):
        """
        We can maybe fetch the tags etc here.
        """
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "schema": {"type": "string"},
                    "database": {"type": "string"},
                    "column_name": {"type": "string"},
                    "column_type": {"type": "string"},
                },
                "required": ["id"],
            },
            "minItems": 1,
        }

    @classmethod
    def _transform(cls, input):
        results = []
        # Renaming the values
        # TODO: This is a hack, we should do this in the discovery query
        # Creating ticket for it.
        for row in input["rows"]:
            results.append(
                {
                    "table": row.get("NAME"),
                    "schema": row.get("SCHEMA"),
                    "database": row.get("DATABASE"),
                    "description": row.get("COL_DESCRIPTION"),
                    "COL_NAME": row.get("COL_NAME"),
                    "COL_TYPE": row.get("COL_TYPE"),
                }
            )
        return results

    @classmethod
    def _after_transform(cls, input):
        """
        Attach id to each row.
        """
        for column in input:
            column["id"] = uuid4().hex
        return input
