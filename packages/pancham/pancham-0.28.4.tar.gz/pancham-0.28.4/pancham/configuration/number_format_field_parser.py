from .field_parser import FieldParser
from pancham.data_frame_field import DataFrameField

class NumberFormatFieldParser(FieldParser):
    """
    Parses field configurations that use a specific number format.

    This class is responsible for identifying and handling fields that have a
    'number_format' function defined. It ensures that the fields are parsed
    with the correct formatting logic as defined in their configurations.

    :ivar function_id: Identifier for the number format function.
    :type function_id: str
    """

    function_id = 'number_format'

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.function_id)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.function_id]
        number_format = properties['format']
        source_name = self.get_source_name(field)
        field[self.FIELD_TYPE_KEY] = str

        def apply_number_format(data: dict) -> str:
            field_value = data[source_name]
            return number_format.format(field_value)

        return self.build_func_field(field, apply_number_format)
