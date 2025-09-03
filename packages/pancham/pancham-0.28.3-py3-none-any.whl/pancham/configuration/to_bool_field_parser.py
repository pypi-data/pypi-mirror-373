from .field_parser import FieldParser
from pancham.data_frame_field import DataFrameField

class ToBoolFieldParser(FieldParser):
    """
    Parses fields with a specified function identifier to convert values to boolean.

    This class is responsible for parsing fields defined with a specific function
    identifier (`to_bool`). Its main purpose is to apply a transformation to data
    fields by converting them into boolean values as per given specifications.

    :ivar function_id: Identifier of the function that defines the behavior of the
        parser for boolean conversion.
    :type function_id: str
    """

    function_id = 'to_bool'

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.function_id)

    def parse_field(self, field: dict) -> DataFrameField:
        if self.get_source_name(field) is None:
            raise ValueError("Source not set")

        return DataFrameField(
            name=field['name'],
            nullable=self.is_nullable(field),
            field_type=int,
            source_name=None,
            func=lambda x: self.__to_bool(field, x),
            cast_type=True
        )

    def __to_bool(self, field: dict, values: dict):
        source = self.get_source_name(field)

        try:
            return bool(values[source])
        except ValueError as e:
            if 'error_value' in field[self.FUNCTION_KEY][self.function_id]:
                error_value = field[self.FUNCTION_KEY][self.function_id]['error_value']

                if type(error_value) == 'str' and error_value.lower() == 'none':
                    return None
                return error_value

            raise e

