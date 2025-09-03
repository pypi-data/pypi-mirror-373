from pancham.configuration.field_parser import FieldParser
from pancham.data_frame_field import DataFrameField
import importlib

class DynamicFieldParser(FieldParser):

    FUNCTION_ID = "dynamic"

    def can_parse_field(self, field: dict) -> bool:
        return self.has_function_key(field, self.FUNCTION_ID)

    def parse_field(self, field: dict) -> DataFrameField:
        """
        Parses a field dictionary to produce a `DataFrameField` object.

        This method extracts the necessary module and class information from the
        field dictionary, dynamically loads the specified class, and uses it to
        create a `FieldParser` instance. The `parse_field` method of the `FieldParser`
        instance is subsequently called to process and return the parsed field.

        :param field:
            A dictionary containing the field definition. The dictionary must include
            keys to locate the module and class used for parsing, as well as the data
            to be parsed.
        :return:
            An instance of `DataFrameField` containing the processed field extracted
            from the provided dictionary.
        """
        properties = field[self.FUNCTION_KEY][self.FUNCTION_ID]

        module_name = properties['module']
        class_name = properties['class']

        module = importlib.import_module(module_name)
        field_class = getattr(module, class_name)
        field_instance: FieldParser = field_class()

        return field_instance.parse_field(field)

