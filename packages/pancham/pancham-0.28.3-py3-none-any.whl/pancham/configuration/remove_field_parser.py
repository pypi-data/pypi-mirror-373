from pancham.data_frame_field import DataFrameField
from .field_parser import FieldParser


class RemoveFieldParser(FieldParser):
    """
    Field parser that identifies and processes the removal of fields in a DataFrame.

    This class is used to parse and construct instances of `DataFrameField` for fields specified
    with a "remove" directive in the input dictionary. Its primary purpose is managing the removal
    of specific columns from a DataFrame based on given configuration.

    :ivar FUNCTION_ID: Identifier used to detect the "remove" function within field definitions.
    :type FUNCTION_ID: str
    """

    FUNCTION_ID = "remove"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        column_name = properties['name']

        return DataFrameField(
            name = column_name,
            nullable=True,
            field_type=str,
            source_name=None,
            df_func=lambda d: d.drop(columns=[column_name], axis=1, inplace=True)
        )