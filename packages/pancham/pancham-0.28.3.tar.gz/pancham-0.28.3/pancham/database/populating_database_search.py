from sqlalchemy import Table

from .database_engine import get_db_engine, META
from .caching_database_search import DatabaseSearch, CachingDatabaseSearch


class PopulatingDatabaseSearch(DatabaseSearch):
    """
    Class for managing and enhancing database searches by facilitating automatic addition
    of search entries into a specified table when a given key does not exist. This class
    utilizes caching for database search queries to improve performance and ensures that
    the missing data is added to the table dynamically. It supports optional type casting
    for both search keys and their corresponding values if specified.

    :ivar table_name: Name of the database table to be queried and modified.
    :type table_name: str
    :ivar search_col: Name of the column used for searching within the database table.
    :type search_col: str
    :ivar value_col: Name of the column used to retrieve result values from the database table.
    :type value_col: str
    :ivar cast_search: Optional type casting for search keys.
    :type cast_search: None | str
    :ivar cast_value: Optional type casting for corresponding values.
    :type cast_value: None | str
    :ivar caching_search: Instance of the caching mechanism for database search queries.
    :type caching_search: CachingDatabaseSearch | None
    """

    def __init__(self, table_name: str, search_col: str, value_col: str, cast_search: None|str = None, cast_value: None|str = None):
        self.table_name = table_name
        self.search_col = search_col
        self.value_col = value_col
        self.cast_search = cast_search
        self.cast_value = cast_value
        self.caching_search = None

    def get_mapped_id(self, search_value: str | int) -> str | int | None:
        if search_value is None:
            return None

        value = self.__get_caching_search().get_mapped_id(search_value)

        if value is None:
            with get_db_engine().engine.connect() as conn:
                data_table = Table(self.table_name, META, autoload_with=conn)
                insert_values = {self.search_col: search_value}
                insert_query = data_table.insert().values(**insert_values)

                conn.execute(insert_query)
                conn.commit()
                self.caching_search = None

                value = self.__get_caching_search().get_mapped_id(search_value)

        return value

    def __get_caching_search(self):
        if self.caching_search is None:
            self.caching_search = CachingDatabaseSearch(
                table_name=self.table_name,
                search_col=self.search_col,
                value_col=self.value_col,
                cast_search=self.cast_search,
                cast_value=self.cast_value
            )

        return self.caching_search