from collections import defaultdict

from sqlalchemy import Table, select, Connection, Select, text, TextClause

from pancham.reporter import get_reporter
from .database_engine import get_db_engine, META

class DatabaseSearch:

    def get_mapped_id(self, search_value: str|int) -> str|int|None:
        """
        Search for a mapped identifier based on the given search value.

        This function takes a search value, which can be either a string or an
        integer, and attempts to find a corresponding mapped identifier. If no match
        is found, it returns None.

        :param search_value: The value to be searched, either a string or integer.
        :type search_value: str | int
        :return: The mapped identifier if found, or None if no match exists.
        :rtype: str | int | None
        """
        pass


    def cast_value(self, value: any, cast_to: None|str) -> str|int:
        """
        Converts a given value to a specified type (string or integer) if applicable.
        The function checks the type to cast to, converts the value accordingly, and returns
        the cast value. If no type casting is indicated, the function returns the value
        unchanged.

        :param value: The input value to be cast.
        :type value: any

        :param cast_to: The desired type casting for the value ("str" or "int") or None
                        if no casting is required.
        :type cast_to: None | str

        :return: The value cast to the specified type or the original value if no
                 casting is requested.
        :rtype: str | int | any
        """
        reporter = get_reporter()

        try:
            if cast_to == 'str':
                reporter.report_debug(f"Casting {value} to string")
                return str(value)

            if cast_to == 'int':
                reporter.report_debug(f"Casting {value} to int")
                return int(value)

        except ValueError:
            reporter.report_debug(f"Value {value} cannot be cast to {cast_to}")

        reporter.report_debug(f"No cast to value set - {cast_to}")

        return value


class CachingDatabaseSearch(DatabaseSearch):
    """
    Implements a caching mechanism for querying and retrieving data from a
    database table. This class aims to improve database query performance by
    storing results from repeated queries into an in-memory cache. The
    user can specify the table name, column names for searching and retrieving
    data, and optional data type casting for search and value columns.

    This class is particularly suited for applications where specific database
    mappings are queried frequently, allowing the results to be cached for
    faster access during subsequent queries.

    :ivar table_name: The name of the database table to query.
    :type table_name: str

    :ivar search_col: The column name in the database table used for searching.
    :type search_col: str

    :ivar value_col: The column name in the database table whose values are
         retrieved.
    :type value_col: str

    :ivar cast_search: Specifies the data type to cast search column values to
         during queries. Valid values are "str", "int", or None.
    :type cast_search: None | str

    :ivar cast_value: Specifies the data type to cast value column values to
         during result retrieval. Valid values are "str", "int", or None.
    :type cast_value: None | str

    :ivar cached_data: Stores key-value mappings retrieved from the database for
         quick access without redundant database queries.
    :type cached_data: dict
    """

    def __init__(self, table_name: str, search_col: str, value_col: str, cast_search: None|str = None, cast_value: None|str = None):
        self.table_name = table_name
        self.search_col = search_col
        self.value_col = value_col
        self.cast_search = cast_search
        self.cast_value_type = cast_value
        self.cached_data = {}

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
        data = self.__load_data()
        reporter = get_reporter()
        reporter.report_debug(f"Reading cached data: {data}")

        search = self.cast_value(search_value, self.cast_search)
        reporter.report_debug(f"Finding id {search} - type {type(search)}")

        if search in data:
            return data[search]

        return None

    def get_query(self, conn: Connection) -> Select|TextClause:
        """
        Create a SQL SELECT query on a specified table, filtering out rows where the
        search column is NULL. This function constructs a SQLAlchemy Select object
        targeting specific columns in the table and applies the appropriate condition.

        :param conn: A SQLAlchemy Connection object used to interact with the database.
        :type conn: Connection
        :return: A SQLAlchemy Select object representing the desired SQL query.
        :rtype: Select
        """
        data_table = Table(self.table_name, META, autoload_with=conn)
        return (select(data_table.c[self.search_col, self.value_col])
                .where(data_table.c[self.search_col].is_not(None))
                .where(data_table.c[self.value_col].is_not(None)))

    def __load_data(self) -> dict[str|int, str|int]:
        """
        Loads data from the database table and caches it for future access. The
        method retrieves rows from the table based on the provided column names
        and performs type casting as per configuration. If data has been cached
        previously, it simply returns the cached data to optimize performance
        by avoiding redundant queries to the database.

        :return: A dictionary mapping search column values to value column values.
        :rtype: dict[str | int, str | int]
        :raises sqlalchemy.exc.SQLAlchemyError: If an error occurs during database
            connection or query execution.
        """
        if len(self.cached_data) > 0:
            return self.cached_data

        with get_db_engine().engine.connect() as conn:
            query = self.get_query(conn)

            res = conn.execute(query).fetchall()

            for row in res:
                key = self.cast_value(row[0], self.cast_search)
                value = self.cast_value(row[1], self.cast_value_type)
                self.cached_data[key] = value

        return self.cached_data

class SQLFileCachingDatabaseSearch(CachingDatabaseSearch):
    """
    A specialized class that extends CachingDatabaseSearch to include SQL file
    functionality.
    """
    def __init__(self, file: str, cast_search: None|str = None, cast_value: None|str = None):
        super().__init__('', '', '', cast_search, cast_value)
        self.file = file

    def get_query(self, conn: Connection) -> Select|TextClause:
        """
        Retrieve and return an SQL query from a file associated with the instance.

        This method reads the content of the SQL file specified by the instance's `file`
        attribute and converts it into a valid SQL query object. The result can be used
        to execute database operations.

        :param conn: A connection object to interact with the database. This parameter is unused in the function but
                     provides context for potential future utilization.
        :type conn: Connection
        :return: A representation of the SQL query read from the file. This can be either a SQLAlchemy `Select`
                 object or a `TextClause` object, depending on the format of the query in the SQL file.
        :rtype: Select | TextClause
        """
        with open(self.file, 'r') as sql_file:
            query = sql_file.read()
            return text(query)

class FilteredCachingDatabaseSearch(CachingDatabaseSearch):
    """
    A specialized class that extends CachingDatabaseSearch to include filtering functionality.

    This class is used to perform database searches with caching
    capabilities while incorporating additional filtering constraints based on a
    provided filter dictionary. The filter conditions are applied to database
    query operations.

    :ivar table_name: The name of the table to query in the database.
    :type table_name: str
    :ivar search_col: The column name used for searching in the database table.
    :type search_col: str
    :ivar value_col: The column name used for retrieving values in the database table.
    :type value_col: str
    :ivar filter: A dictionary containing key-value pairs for filtering query
        results; keys represent column names and values represent the corresponding
        required values.
    :type filter: dict[str, str]
    :ivar cast_search: Optional type casting for the search column used in the
        database query. Defaults to None.
    :type cast_search: str or None
    :ivar cast_value: Optional type casting for the value column used in the
        database query. Defaults to None.
    :type cast_value: str or None
    """

    def __init__(self, table_name: str, search_col: str, value_col: str, filter: dict[str, str], cast_search: None|str = None, cast_value: None|str = None):
        super().__init__(table_name, search_col, value_col, cast_search, cast_value)
        self.filter = filter

    def get_query(self, conn: Connection) -> Select:
        data_table = Table(self.table_name, META, autoload_with=conn)
        select_query = select(data_table.c[self.search_col, self.value_col]).where(data_table.c[self.search_col].is_not(None))
        reporter = get_reporter()

        for k, v in self.filter.items():
            select_query = select_query.where(data_table.c[k] == v)

        reporter.report_debug(f"Generated query: {str(select_query)}")
        return select_query

