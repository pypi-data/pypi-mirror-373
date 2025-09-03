from pancham.data_frame_field import DataFrameField
from .field_parser import FieldParser


class StaticFieldParser(FieldParser):
    """
    StaticFieldParser is a specific implementation of FieldParser intended for parsing fields
    characterized by a 'static' function key. This parser is tailored to work with field
    definitions containing the 'static' functionality and utilizes the base class's
    functionality to handle parsing operations.

    Configuration:

    func:
        static:
            value: <Value to return>
    """

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, 'static')

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY]['static']

        if 'value' not in properties:
            raise ValueError('Value not set')

        return DataFrameField(
            name=field['name'],
            nullable=True,
            source_name=None,
            field_type=field[self.FIELD_TYPE_KEY],
            func=lambda x: properties['value']
        )