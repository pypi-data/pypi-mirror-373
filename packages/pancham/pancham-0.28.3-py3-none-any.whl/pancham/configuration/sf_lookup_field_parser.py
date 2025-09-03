from pancham.data_frame_field import DataFrameField
from pancham.integration.salesforce_lookup import SalesforceLookup
from .field_parser import FieldParser


class SFLookupFieldParser(FieldParser):
    """
    Handles parsing of fields with a "Salesforce lookup" function identifier.

    This class is a specialized implementation of `FieldParser` designed to
    support fields with the Salesforce lookup functionality. It checks whether
    a field has the required structure and extracts parameters necessary to
    perform a Salesforce lookup operation. The parsing involves constructing
    a function field that retrieves mapped identifiers from Salesforce based
    on query, search column, and value column specifications in the input field.

    :ivar FUNCTION_ID: Identifier for the Salesforce lookup function used in the field.
    :type FUNCTION_ID: str
    """

    FUNCTION_ID = "sf_lookup"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]
        query = properties['query']
        search_column = properties['search_column']
        value_column = properties['value_column']

        lookup = SalesforceLookup(query)

        def sf_lookup(data: dict) -> str|None:
            value = data[self.get_source_name(field)]

            return lookup.get_mapped_id(search_column=search_column, value = value, value_column=value_column)

        return self.build_func_field(field, sf_lookup)
