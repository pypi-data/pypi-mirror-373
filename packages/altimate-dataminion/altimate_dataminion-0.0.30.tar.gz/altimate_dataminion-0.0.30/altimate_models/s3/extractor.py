from altimate_models.duckdb.extractor import DuckDBExtractor


class S3Extractor(DuckDBExtractor):

    def _initialize(self):
        if self.engine:
            return
        try:
            self.engine = self._create_engine(self.connection_str)
        except Exception:
            raise Exception("Could not connect to S3 with the provided credentials.")