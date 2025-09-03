from .field_parser import FieldParser
from pancham.data_frame_field import DataFrameField

class MatchFieldParser(FieldParser):
    """
    Match a column to a known value and set the value as true if they match

    Configuration:

    func:
        eq:
            source_name: <Name of col to consider>
            match: <Value to compare to source name value>

    This class provides functionality to determine whether a field can be parsed
    and to parse the field accordingly. It is used to handle fields where a
    matching condition is specified and to generate the corresponding
    `DataFrameField` object.

    :ivar attribute1: Description of attribute1.
    :type attribute1: type
    :ivar attribute2: Description of attribute2.
    :type attribute2: type
    """

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, 'eq')

    def parse_field(self, field: dict) -> DataFrameField:
        is_properties = field['func']['eq']

        if 'source_name' not in is_properties or 'match' not in is_properties:
            raise ValueError('Is func requires source_name and match')

        return DataFrameField(
            name=field['name'],
            nullable=self.is_nullable(field),
            source_name=None,
            field_type=bool,
            func=lambda x: x[is_properties['source_name']] == is_properties['match']
        )