import pandas as pd

from pancham.database.caching_database_search import DatabaseSearch
from pancham.database.database_search_manager import get_database_search
from pancham.data_frame_field import DataFrameField
from pancham.reporter import get_reporter
from .field_parser import FieldParser

class DatabaseMatchFieldParser(FieldParser):
    """
    Map database fields

    Configuration:

    func:
        database_match:
            table_name: <Name of the table to search>
            search_column: <Name of the column to search>
            value_column: <Name of the column to find the value>
            search_cast: <Optional, str or int, set if we need to cast the search column>
            value_cast: <Optional, str or int, set if we need to cast the value column>

    :ivar FUNCTION_ID: Identifier for the 'database_match' function.
    :type FUNCTION_ID: str
    :ivar TABLE_NAME_KEY: Key used to extract the table name from the field properties.
    :type TABLE_NAME_KEY: str
    :ivar SEARCH_COLUMN_KEY: Key denoting the column in the table used for searching.
    :type SEARCH_COLUMN_KEY: str
    :ivar VALUE_COLUMN_KEY: Key denoting the column in the table used for value retrieval.
    :type VALUE_COLUMN_KEY: str
    :ivar SEARCH_CAST_VALUE_KEY: Key specifying the cast type for search column values.
    :type SEARCH_CAST_VALUE_KEY: str
    :ivar VALUE_CAST_VALUE_KEY: Key specifying the cast type for value column values.
    :type VALUE_CAST_VALUE_KEY: str
    """

    FUNCTION_ID = "database_match"
    TABLE_NAME_KEY = "table_name"
    SEARCH_COLUMN_KEY = "search_column"
    VALUE_COLUMN_KEY = "value_column"
    SEARCH_CAST_VALUE_KEY = "search_cast"
    VALUE_CAST_VALUE_KEY = "value_cast"
    FILTER_KEY = "filter"
    POPULATE_KEY = "populate"
    STATIC_VALUE_KEY = "static"
    SQL_FILE_KEY = "sql_file"
    CACHE_METHOD_KEY = "cache_method"
    FIXTURE_KEY = "fixture_key"
    fixture_map = {}

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        if self.TABLE_NAME_KEY not in properties or self.SEARCH_COLUMN_KEY not in properties or self.VALUE_COLUMN_KEY not in properties:
            raise ValueError("Missing required properties for database_match function.")

        filter_value = properties.get(self.FILTER_KEY, None)
        reporter = get_reporter()
        mapped_filtered = {}
        database_search: DatabaseSearch|None = None

        def build_database_search() -> DatabaseSearch:
            """
            Builds and configures a `DatabaseSearch` object based on provided filters and properties.

            This method initializes and returns a `DatabaseSearch` instance. If `database_search`
            is not already set, it evaluates filters and maps filter values as needed. It handles
            values directly as well as those requiring additional processing, including resolving
            through fixture maps or extracting search-related data.

            Attributes
            ----------
            database_search : DatabaseSearch
                Configured `DatabaseSearch` instance. Initializes if `None`.
            mapped_filtered : dict
                Dictionary of mapped filter values derived from `filter_value`.

            Returns
            -------
            DatabaseSearch
                A configured `DatabaseSearch` object initialized with the provided filters.

            Parameters
            ----------
            None

            Raises
            ------
            None

            Notes
            -----
            - The method processes `filter_value` to map filters into `mapped_filtered`.
            - For complex values in `filter_value`, it resolves fixture keys or search values.
            - Updates the `fixture_map` with resolved identifiers for future references.
            """
            nonlocal database_search, mapped_filtered
            if database_search is None:
                if filter_value and len(mapped_filtered) == 0:
                    reporter.report_debug(f'Filter value {filter_value}')
                    for key, value in filter_value.items():
                        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                            mapped_filtered[key] = value
                        else:
                            fixture_key = value.get(self.FIXTURE_KEY, None)
                            if fixture_key is not None and fixture_key in self.fixture_map:
                                mapped_filtered[key] = self.fixture_map[fixture_key]
                                reporter.report_debug(f'Using fixture value {mapped_filtered[key]} for {key}')
                                continue

                            filter_search = self.__build_search_value(value)

                            # Value of the search should always be a static
                            search_value = self.__get_search_value({}, value)
                            filter_id = filter_search.get_mapped_id(search_value)
                            mapped_filtered[key] = filter_id
                            reporter.report_debug(f'Using filter value {filter_id} for {key}')

                            if fixture_key is not None:
                                self.fixture_map[fixture_key] = filter_id

                database_search = self.__build_search_value(properties, filter=mapped_filtered)

            return database_search

        def map_value(data: dict|pd.Series) -> str:
            if isinstance(data, pd.Series):
                data = data.to_dict()

            search = build_database_search()
            search_value = self.__get_search_value(data, properties)

            mapped_id = search.get_mapped_id(search_value)
            reporter.report_debug(f'Database search {search_value} mapped to {mapped_id}')

            return mapped_id

        return self.build_func_field(
            field=field,
            func=map_value
        )

    def __build_search_value(self, properties: dict, filter: dict[str, str]|None = None) -> DatabaseSearch:

        populate = properties.get(self.POPULATE_KEY, False)
        search_cast = properties.get(self.SEARCH_CAST_VALUE_KEY, None)
        value_cast = properties.get(self.VALUE_CAST_VALUE_KEY, None)
        sql_file = properties.get(self.SQL_FILE_KEY, None)
        cache_method = properties.get(self.CACHE_METHOD_KEY, 'dict')

        if filter and len(filter) > 0:
            filter_value = filter
        else:
            filter_value = properties.get(self.FILTER_KEY, None)

        return get_database_search(
            table_name=properties.get(self.TABLE_NAME_KEY, ''),
            search_col=properties.get(self.SEARCH_COLUMN_KEY, ''),
            value_col=properties.get(self.VALUE_COLUMN_KEY, ''),
            cast_search=search_cast,
            cast_value=value_cast,
            filter=filter_value,
            populate=populate,
            sql_file=sql_file,
            cache_method=cache_method
        )

    def  __get_search_value(self, data: dict, properties: dict[str, str]) -> str:
        """
        Retrieve the search value from the given data and properties based on specific keys.

        This method determines whether to extract a value directly from the `properties`
        dictionary or to use it as a reference to obtain a value from the `data` dictionary.
        If the `STATIC_VALUE_KEY` is present in the `properties`, the corresponding
        value in `properties` is returned. Otherwise, the value associated with
        `properties[self.SOURCE_NAME_KEY]` in `data` is returned.

        :param data: Input data dictionary containing potential values.
        :type data: dict
        :param properties: Dictionary of property keys and their associated values.
        :type properties: dict[str, str]
        :return: Extracted search value based on provided data and properties.
        :rtype: str
        """
        if self.STATIC_VALUE_KEY in properties:
            return properties[self.STATIC_VALUE_KEY]

        return data[properties[self.SOURCE_NAME_KEY]]

    def __get_fixture_key(self, value: dict) -> str:
        """
        Retrieve the fixture key from the given value.
        """
