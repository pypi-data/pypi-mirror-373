from pancham.data_frame_field import DataFrameField
from .field_parser import FieldParser
import re

class RegexExtractFieldParser(FieldParser):
    """
    A parser class for processing a field using a regular expression
    extraction method.

    This class inherits from FieldParser and provides methods to check if
    a field can be parsed using the regex_extract function and to perform
    the parsing operation itself.
    """

    FUNCTION_ID = "regex_extract"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        source_name = self.get_source_name(field)
        pattern = properties['pattern']
        field[self.FIELD_TYPE_KEY] = bool

        def regex_extract(data: dict) -> str|None:
            value = data[source_name]

            if not isinstance(value, str):
                return None

            match = re.search(pattern, value)

            if match:
                return match.group(1)

            return None

        return self.build_func_field(field, regex_extract)