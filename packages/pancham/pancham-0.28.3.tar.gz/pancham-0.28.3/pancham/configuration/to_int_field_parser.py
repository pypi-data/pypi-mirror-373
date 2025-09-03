from .field_parser import FieldParser
from pancham.data_frame_field import DataFrameField

class ToIntFieldParser(FieldParser):
    """
    Convert a value to an integer

    Configuration:

    func:
        to_int:
            source_name: <Name of col to convert>
            error_value: <Optional value to return if there is an error, if not set then an exception is raised>

    :ivar function_id: Identifier for the parsing function used to recognize
        if the field can be processed by this parser.
    :type function_id: str
    """

    function_id = 'to_int'

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
            func=lambda x: self.__to_int(field, x),
            cast_type=True
        )

    def __to_int(self, field: dict, values: dict):
        source = self.get_source_name(field)

        try:
            return int(values[source])
        except ValueError as e:
            if 'error_value' in field[self.FUNCTION_KEY][self.function_id]:
                error_value = field[self.FUNCTION_KEY][self.function_id]['error_value']

                if type(error_value) == 'str' and error_value.lower() == 'none':
                    return None
                return error_value

            raise e

