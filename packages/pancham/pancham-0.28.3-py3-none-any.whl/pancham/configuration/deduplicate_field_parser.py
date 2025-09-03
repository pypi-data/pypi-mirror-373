import pandas as pd

from pancham.data_frame_field import DataFrameField
from pancham.reporter import get_reporter
from .field_parser import FieldParser


class DeduplicateFieldParser(FieldParser):
    """
    Class responsible for parsing fields with deduplication functionality.

    This class extends the FieldParser and is tailored to handle fields that require
    deduplication. It determines if a field can be processed based on specific criteria
    and parses it into a DataFrameField object, which includes a deduplication function
    to apply on data.

    :ivar FUNCTION_ID: Identifier for the deduplication functionality.
    :type FUNCTION_ID: str
    """

    FUNCTION_ID = "deduplicate"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        """
        Parses a dictionary representing a field and returns a DataFrameField object
        based on the field's properties and configuration. This includes determining
        its name, type, source information, and applying a deduplication function.

        :param field: Dictionary containing field details and configuration settings.
                      It must include the keys required to extract the field name,
                      field type, and its deduplication properties.
        :type field: dict
        :return: A DataFrameField object containing the parsed field's information
                 including its name, type, nullable status, source, and a deduplication
                 function to operate on associated DataFrame data.
        :rtype: DataFrameField
        """
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        def apply_deduplicate(data: pd.DataFrame) -> pd.DataFrame:
            reporter = get_reporter()
            if 'sort_by' in properties:
                sort_values = [properties[self.SOURCE_NAME_KEY]]
                sort_by_key = properties.get('sort_by', None)
                if isinstance(sort_by_key, list):
                    sort_values.extend(sort_by_key)
                else:
                    sort_values.append(sort_by_key)

                ascending = properties.get('ascending', True)

                data = data.sort_values(by=sort_values, ascending=ascending)

            output = data.drop_duplicates(subset=[properties[self.SOURCE_NAME_KEY]], keep='first')
            reporter.report_debug(f'Deduplicate outcome {output}')

            return output

        return DataFrameField(
            name = field['name'],
            field_type=field[self.FIELD_TYPE_KEY],
            nullable=True,
            source_name=self.get_source_name(field),
            df_func=apply_deduplicate
        )