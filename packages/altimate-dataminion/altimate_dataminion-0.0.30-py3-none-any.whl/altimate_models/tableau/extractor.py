class TableauExtractor:
    def __init__(self, connection_str=None, data_source=None):
        self.connection_str = connection_str
        self.data_source = data_source

    def test(self):
        return self.data_source.test_connection()
