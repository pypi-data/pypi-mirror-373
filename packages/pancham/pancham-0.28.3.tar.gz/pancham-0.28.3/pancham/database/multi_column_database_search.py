import math

from sqlalchemy import Table, select

from pancham.configuration.field_parser import FieldParser
from pancham.tool.str_tools import remove_and_split
from .database_engine import get_db_engine, META


class MultiColumnDatabaseSearch:
    """
    Search a database using multiple columns
    """

    SEARCH_COLUMN_KEY = "search_column"
    VALUE_KEY = "value"
    TYPE_KEY = "type"

    def __init__(self, table_name: str, value_col: str, cast_value: None|str = None):
        self.table_name = table_name
        self.value_col = value_col
        self.cast_value = cast_value

    def get_mapped_id(self, search: dict[str, str|int|bool]) -> str|int|None:
        """
        Maps the provided search dictionary to a value from the database table.
        The function uses the key-value pairs in the `search` dictionary to construct
        a SQL query that matches the specified conditions. If a match is found, it
        returns the value from the specified column (`self.value_col`) of the
        database table. If no matches are found, it returns None.

        :param search: A dictionary representing filtering conditions with keys
            as column names and values as the corresponding values to match
            in the database table.
        :type search: dict[str, str | int | bool]

        :return: The value from the specified column if a matching row is found.
            Returns None if no matches are found.
        :rtype: str | int | None
        """

        if len(search) == 0:
            return None

        with get_db_engine().engine.connect() as conn:
            data_table = Table(self.table_name, META, autoload_with=conn)

            query = select(data_table.c[self.value_col])

            for k, v in search.items():
                query = query.where(data_table.c[k] == v)

            res = conn.execute(query).fetchall()

            if len(res) == 0:
                return None

            return res[0][0]

    def build_search_values(self, data: dict, search_options: list[dict[str, str|list[dict[str, str|int]]]]) -> dict[str, str|int|bool]:
        """
        Builds a dictionary of search values based on the provided data and search options.

        This method processes the given data and search options to construct a dictionary
        of search values by evaluating each search option. The search options dictate how
        data is transformed or extracted, depending on the type of operation specified.

        :param data: Dictionary containing source data required to extract or generate
            search values. This should include keys anticipated by the search options.
        :type data: dict
        :param search_options: A list of configuration dictionaries that define how the
            search values are to be evaluated. Each configuration dictionary describes a
            type of operation (e.g., static, field, split), necessary keys, and processing
            rules.
        :type search_options: list[dict[str, str | list[dict[str, str | int]]]]
        :return: A dictionary containing the processed search values. The keys correspond
            to column names, and values are data derived or extracted as per the
            `search_options`.
        :rtype: dict[str, str | int | bool]
        :raises ValueError: If an unsupported search type is provided in a search option.
        """
        search_values = {}
        for search_option in search_options:
            field_type = search_option[self.TYPE_KEY]

            if field_type == "static":
                column = search_option[self.SEARCH_COLUMN_KEY]
                search_values[column] = search_option[self.VALUE_KEY]

            elif field_type == "field":
                column = search_option[self.SEARCH_COLUMN_KEY]
                search_values[column] = data[search_option[FieldParser.SOURCE_NAME_KEY]]

            elif field_type == "split":
                split_values = self.__build_search_value(search_option, data)

                search_values = search_values | split_values

            else:
                raise ValueError(f"Unsupported search type: {search_option['type']}")

        return search_values
    
    def __build_search_value(self, search_option: dict[str, str], data: dict) -> dict:
        split_char = search_option["split_char"]
        remove_pattern = search_option.get("remove_pattern", None)
        source = data[search_option[FieldParser.SOURCE_NAME_KEY]]

        fields = remove_and_split(source, split_char, remove_pattern)
        search_values = {}
        for match in search_option["matches"]:
            field_index = match["field_index"]
            if len(fields) <= field_index:
                continue

            field_value = fields[field_index]

            if field_value is None:
                continue

            if (isinstance(field_value, int) or isinstance(field_value, float)) and math.isnan(field_value):
                continue

            column = match[self.SEARCH_COLUMN_KEY]
            search_values[column] = fields[field_index]

        return search_values

