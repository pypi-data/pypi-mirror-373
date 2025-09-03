from pancham.data_frame_field import DataFrameField
from .field_parser import FieldParser


class ConcatFieldParser(FieldParser):
    """
    Docs - https://github.com/Loqui-Tech/pancham/wiki/Concat

    Parses fields that use the 'concat' function ID in a DataFrameField.

    This class is responsible for identifying if a field contains the
    specified 'concat' function and then uses its details to construct a
    DataFrameField. The 'concat' function combines data from multiple
    fields into a single string, with an optional separator that can
    be customized through the 'join' property. If 'join' is not specified,
    it defaults to a space (' ').

    :ivar FUNCTION_ID: The identifier for the 'concat' function.
    :type FUNCTION_ID: str
    """

    FUNCTION_ID = "concat"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        concat_field_keys = properties['fields']
        join = properties.get('join', ' ')
        trim_ends = properties.get('trim_ends', False)
        trim_all = properties.get('trim_all', False)

        def concat_fields(data: dict):
            values = []
            for f in concat_field_keys:
                field_value = data[f]
                if type(field_value) is not str:
                    continue

                if trim_all:
                    field_value = field_value.strip()
                values.append(field_value)

            joined_values = join.join(values)

            if trim_ends or trim_all:
                joined_values = joined_values.strip()

            return joined_values

        return DataFrameField(
            name = field['name'],
            field_type=str,
            nullable=self.is_nullable(field),
            source_name=None,
            func=concat_fields
        )