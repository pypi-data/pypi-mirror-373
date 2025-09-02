class TableDoesNotExists(Exception):
    """
    Exception when plugin is configured with table which does not exists
    anymore. For example developer changed name or application providing
    that table is not used anymore.
    """

    def __init__(self, table_name: str) -> None:
        super().__init__()
        self.table_name = table_name
