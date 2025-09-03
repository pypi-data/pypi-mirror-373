from .field_parser import FieldParser
from pancham.data_frame_field import DataFrameField
from pancham.database.multi_column_database_search import MultiColumnDatabaseSearch

class DatabaseMultiFieldSearchParser(FieldParser):
    """
    Handles parsing of database fields with multiple search options.

    func:
        database_multi_field_search:
            table_name: <Name of the table>
            value_column: <Column containing the value to search for>
            search:
                - type: static
                  search_column: <Column to search>
                  value: <Static value to search>
                - type: field
                  search_column: <Column to search>
                  source_name: <Data field name to load>


    :ivar FUNCTION_ID: A unique identifier for the parser, indicating it
        supports database fields with multiple search capabilities.
    :type FUNCTION_ID: str
    """

    FUNCTION_ID = "database_multi_field_search"
    TABLE_NAME_KEY = "table_name"
    SEARCH_KEY = "search"
    SEARCH_COLUMN_KEY = "search_column"
    VALUE_COLUMN_KEY = "value_column"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        field_properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        if self.TABLE_NAME_KEY not in field_properties or self.SEARCH_KEY not in field_properties or self.VALUE_COLUMN_KEY not in field_properties:
            raise ValueError(f"Missing required properties for {self.FUNCTION_ID} function.")

        table_name = field_properties[self.TABLE_NAME_KEY]
        value_column = field_properties[self.VALUE_COLUMN_KEY]
        search_options = field_properties[self.SEARCH_KEY]

        def map_value(data: dict) -> str:
            search = MultiColumnDatabaseSearch(table_name, value_column)
            search_values = search.build_search_values(data, search_options)

            return search.get_mapped_id(search_values)


        return self.build_func_field(
            field=field,
            func=map_value
        )