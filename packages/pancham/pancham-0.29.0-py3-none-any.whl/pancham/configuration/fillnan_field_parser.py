import pandas as pd

from pancham.data_frame_field import DataFrameField
from pancham.reporter import get_reporter
from .field_parser import FieldParser

class FillNanFieldParser(FieldParser):


    FUNCTION_ID = "fill_nan"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        def apply_fill(data: pd.DataFrame) -> pd.DataFrame:
            replace_value = properties.get('replace_value', None)
            source = self.get_source_name(field)

            data[source] = data[source].fillna(replace_value)

            return data

        return DataFrameField(
            name = field['name'],
            field_type=field[self.FIELD_TYPE_KEY],
            nullable=self.is_nullable(field),
            source_name=self.get_source_name(field),
            df_func=apply_fill
        )