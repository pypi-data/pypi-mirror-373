from pancham.data_frame_field import DataFrameField
from .field_parser import FieldParser


class PartTextExtractorParser(FieldParser):
    """
    Extract part of a text field by splitting the content and removing values

    func:
        split_extract:
            splitter: <String to split around e.g. , or ' '>
            return_index: <Int Index of the string to return>
            split_limit: <Optional Int Limit the number of splits>
            remove: <Optional list of strings to be removed from the source string>
            minimum_expected_parts: <Optional Int if there are less than this number of parts return the error value>
            error_value: <Optional value to return if there is an error ('input' will return whole string)>
            length_return_values: <List of lengths that return a specific value>
                - length: <Int length after split>
                  value: <String|Int fixed value to return>
                  return_type: <'index' if value is an index to return, 'input' if return value should be whole input>

    :ivar attribute1: Description of attribute1.
    :type attribute1: type
    :ivar attribute2: Description of attribute2.
    :type attribute2: type
    """

    FUNCTION_ID = 'split_extract'
    SPLITTER = 'splitter'
    RETURN_INDEX = 'return_index'
    REMOVE = 'remove'
    MINIMUM_EXPECTED_PARTS = 'minimum_expected_parts'
    ERROR_VALUE = 'error_value'
    LENGTH_RETURN_VALUES = 'length_return_values'
    LENGTH = 'length'
    VALUE = 'value'
    SPLIT_LIMIT = 'split_limit'
    RETURN_TYPE = 'return_type'

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        def extract_value(input: dict) -> str|None:
            return_index = properties[self.RETURN_INDEX]
            minimum_parts = properties.get(self.MINIMUM_EXPECTED_PARTS, return_index)
            max_split = properties.get(self.SPLIT_LIMIT, -1)

            if self.SPLITTER not in properties or self.RETURN_INDEX not in properties:
                raise ValueError('Splitter and return index required')

            raw_input = input[self.get_source_name(field)]

            if not isinstance(raw_input, str):
                return None

            clean_input = raw_input.strip()

            if self.REMOVE in properties:
                for remove in properties[self.REMOVE]:
                    clean_input = clean_input.replace(remove, '')

            input_parts = clean_input.strip().split(properties[self.SPLITTER], max_split)

            if self.LENGTH_RETURN_VALUES in properties:
                for length_return_value in properties[self.LENGTH_RETURN_VALUES]:
                    if length_return_value[self.LENGTH] == len(input_parts):
                        return_type = length_return_value.get(self.RETURN_TYPE, '')
                        if return_type == 'input':
                            return clean_input
                        elif return_type == 'index':
                            return input_parts[length_return_value[self.VALUE]]
                        else:
                            return length_return_value[self.VALUE]

            if len(input_parts) >= minimum_parts:
                return input_parts[return_index]

            if self.ERROR_VALUE in properties:
                error_value = properties[self.ERROR_VALUE]

                if error_value == 'input':
                    return clean_input

                return error_value

            return None

        return DataFrameField(
            name=field['name'],
            nullable = self.is_nullable(field),
            source_name=None,
            field_type=str,
            func=extract_value
        )