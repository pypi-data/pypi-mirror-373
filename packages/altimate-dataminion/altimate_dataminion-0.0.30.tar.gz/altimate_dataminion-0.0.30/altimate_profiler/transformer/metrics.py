import decimal
from uuid import uuid4

from altimate_profiler.transformer.base import Transformer


class MetricTransformer(Transformer):
    """
    Transforms the metrics collected by the MetricsCollectorJob into JSON Output
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
        TODO: Value of the metric value should be of the correct type
        """
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "table_name": {"type": "string"},
                    "schema": {"type": "string"},
                    "database": {"type": "string"},
                    "column_name": {"type": "string"},
                    "metric": {"type": "string"},
                    "value": {"type": "string"},
                    "time_window_start": {"type": "string"},
                    "time_window_end": {"type": "string"},
                },
                "required": ["id"],
            },
            "minItems": 1,
        }

    @classmethod
    def _transform(cls, inputs):
        """
        Transform the input into the normalized schema.
        """
        result = []
        for input in inputs:
            for row in input["rows"]:
                for column in input["columns"]:
                    result.append(
                        {
                            "is": float(row[column])
                            if type(row[column]) == decimal.Decimal
                            else row[column],
                        }
                    )
        return result

    @classmethod
    def _after_transform(cls, input):
        """
        Attach id to each row.
        """
        for metric in input:
            metric["id"] = uuid4().hex
        return {"terms": input}
