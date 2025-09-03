import functools

from sqlalchemy import Table, select

from pancham.database.caching_database_search import DatabaseSearch
from pancham.database.database_engine import get_db_engine, META
from pancham.reporter import get_reporter

@functools.cache
def get_db_value(table_name: str, search_col: str, value_col: str, search_value: str|int) -> str|int|None:
    with get_db_engine().engine.connect() as conn:
        data_table = Table(table_name, META, autoload_with=conn)
        query = select(data_table.c[search_col, value_col]).where(data_table.c[search_col] == search_value).limit(1)
        res = conn.execute(query).fetchone()

        if res is None:
            return None

        return res[1]

class PyDatabaseCacheSearch(DatabaseSearch):
    """
    Handles database search operations with caching capabilities.

    This class extends the functionality of `DatabaseSearch` to include additional
    caching mechanisms and provides utilities for retrieving mapped values from a
    database table based on a search key.
    """

    def __init__(self, table_name: str, search_col: str, value_col: str, cast_search: None|str = None, cast_value: None | str = None):
        self.table_name = table_name
        self.search_col = search_col
        self.value_col = value_col
        self.cast_search = cast_search
        self.cast_value_type = cast_value

    def get_mapped_id(self, search_value: str|int) -> str|int|None:
        """
        Retrieves the mapped value corresponding to the provided search key.

        This method looks up the given `search_value` in the data dictionary. If the
        search key exists in the dictionary, the corresponding value is returned.
        If the search key is not found, the method returns `None`.

        :param search_value: The key for which the mapped value needs to be retrieved,
            which can be of type `str` or `int`.
        :return: Mapped value associated with the provided search key if found,
            which can be of type `str` or `int`. Returns `None` if the key is not found.
        """
        reporter = get_reporter()
        reporter.report_debug(f"Reading non-cached data")

        value = get_db_value(self.table_name, self.search_col, self.value_col, self.cast_value(search_value, self.cast_search))
        return self.cast_value(value, self.cast_value_type)
