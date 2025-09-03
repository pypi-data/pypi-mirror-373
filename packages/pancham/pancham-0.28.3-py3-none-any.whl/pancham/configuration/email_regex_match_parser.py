from pancham.data_frame_field import DataFrameField
from .field_parser import FieldParser
import re

class EmailRegexMatchParser(FieldParser):
    """
    This class parses fields to identify and construct a regex-matching function
    for specifically validating email addresses.

    The class utilizes a predefined email regex pattern to determine whether a given
    field matches the expected email format. It is designed to integrate this validation
    functionality as a field attribute in the data framework system.

    :ivar FUNCTION_ID: Identifier for the specific field-parsing function.
    :type FUNCTION_ID: str
    :ivar PATTERN: Regular expression pattern for matching email addresses.
    :type PATTERN: str
    """

    FUNCTION_ID = "email_match"
    PATTERN = r"^[a-z0-9_\.-]+@[\da-z\.-]+\.[a-z\.]{2,6}$"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:

        source_name = self.get_source_name(field)
        field[self.FIELD_TYPE_KEY] = bool

        def regex_match(data: dict) -> bool:
            value = data[source_name]

            if not isinstance(value, str):
                return False

            return bool(re.search(self.PATTERN, value))

        return self.build_func_field(field, regex_match)