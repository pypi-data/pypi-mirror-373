from .field_parser import FieldParser
from pancham.data_frame_field import DataFrameField


class TextFieldParser(FieldParser):

    def can_parse_field(self, field: dict) -> bool:
        return 'name' in field and 'source_name' in field and 'field_type' in field and field['field_type'] != 'datetime' and 'func' not in field

    def parse_field(self, field: dict) -> DataFrameField:
        field_type = str
        if 'field_type' in field and field['field_type'] == 'int':
            field_type = int

        return DataFrameField(field['name'], field['source_name'], field_type, self.is_nullable(field))