import datetime
import pandas as pd
from typing_extensions import Literal

from .field_parser import FieldParser
from pancham.data_frame_field import DataFrameField

class DateTimeFieldParser(FieldParser):
    """
    Parses fields containing datetime data into a standardized DataFrame format.

    This class is designed to parse fields with datetime information specified
    using a 'datetime' function identifier. It supports custom datetime formats
    and user-specified error-handling behavior when parsing fails.

    :ivar FUNCTION_ID: Identifier that specifies this parser processes fields
        with datetime data.
    :type FUNCTION_ID: str
    """

    FUNCTION_ID = "datetime"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        format = '%d/%m/%Y'
        on_error: Literal['coerce', 'ignore', 'raise'] = 'raise'

        if type(field[self.FUNCTION_KEY][self.FUNCTION_ID]) is dict:
            format = field[self.FUNCTION_KEY][self.FUNCTION_ID].get('format', '%d/%m/%Y')

            on_error = field[self.FUNCTION_KEY][self.FUNCTION_ID].get('on_error', 'raise')
            if on_error not in ['coerce', 'ignore', 'raise']:
                on_error = 'raise'

        def parse_datetime(data: dict) -> datetime.datetime|None:
            try:
                return pd.to_datetime(data[self.get_source_name(field)], format=format)
            except ValueError as e:
                if on_error == 'ignore':
                    return None
                else:
                    raise e

        return DataFrameField(
            name = field['name'],
            field_type=field.get('field_type', datetime.datetime),
            nullable=self.is_nullable(field),
            source_name=None,
            func=parse_datetime
        )