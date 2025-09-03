from pancham.data_frame_field import DataFrameField
from .field_parser import FieldParser
import re

class RegexMatchFieldParser(FieldParser):
    """
    Parses a field using regular expression matching functionality.

    This class provides a mechanism to parse and process fields in a data
    structure by applying a regular expression match function. It checks if
    the specific parsing function is applicable for the provided field and
    builds a corresponding functional field for further processing.

    :ivar FUNCTION_ID: Identifier for the regex match function.
    :type FUNCTION_ID: str
    """

    FUNCTION_ID = "regex_match"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        source_name = self.get_source_name(field)
        pattern = properties['pattern']
        field[self.FIELD_TYPE_KEY] = bool

        def regex_match(data: dict) -> bool:
            value = data[source_name]

            if not isinstance(value, str):
                return False
            
            return bool(re.search(pattern, value))

        return self.build_func_field(field, regex_match)