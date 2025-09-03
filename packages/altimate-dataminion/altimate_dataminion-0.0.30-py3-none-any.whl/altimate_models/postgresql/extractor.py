from altimate_models.base.extractor import SQLAlchemyExtractor


class PostgreSQLExtractor(SQLAlchemyExtractor):
    def _initialize(self):
        super()._initialize()

        try:
            self.connection.execution_options(
                postgresql_readonly=True,
            )
        except Exception:
            raise
