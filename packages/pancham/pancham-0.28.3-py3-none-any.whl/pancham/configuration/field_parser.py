from typing import Callable

import pandas as pd

from pancham.data_frame_field import DataFrameField


class FieldParser:
    """
    Responsible for validating and parsing field data into a structured format.

    This class provides the functionality to determine if a given dictionary
    representing a field adheres to the required schema and to transform it
    into a structured DataFrameField object. It ensures that input fields are
    correctly formatted before being processed in the application.
    """

    FUNCTION_KEY = 'func'
    SOURCE_NAME_KEY = 'source_name'
    FIELD_TYPE_KEY = 'field_type'
    NAME_KEY = 'name'
    CAST_KEY = 'cast'

    def can_parse_field(self, field: dict) -> bool:
        """
        Determines whether the specified field meets the parsing requirements.

        Evaluates the field dictionary to check if it conforms to the rules necessary
        for parsing. This method does not perform the parsing itself but provides
        a validation mechanism for prerequisites.

        :param field: A dictionary representing the input field to be evaluated.
        :return: Returns True if the field meets the parsing conditions, otherwise False.
        """
        pass

    def parse_field(self, field: dict) -> DataFrameField:
        """
        Parses a given dictionary into a DataFrameField.

        This method is used to convert a dictionary representation of a field into a
        DataFrameField object, which is used internally for processing and maintaining
        data schema consistency. It ensures that the input dictionary is correctly
        structured and adheres to the expected formats required by the application.

        :param field:
            A dictionary containing the definition of a DataFrameField.
            The dictionary keys and values must conform to the expected schema.
        :return:
            A DataFrameField object that represents the parsed structure
            of the input dictionary.
        """
        pass

    def is_nullable(self, field: dict) -> bool:
        """
        Determines whether the given field dictionary has a 'nullable' attribute set to True.
        This internal utility is used to check the nullability of a specified field.

        :param field: A dictionary representing the field, expected to contain a 'nullable' key.
        :type field: dict
        :return: A boolean value indicating if the 'nullable' key exists in the dictionary
                 and its value is True.
        :rtype: bool
        """
        return 'nullable' in field and field['nullable'] is True

    def is_function(self, field: dict) -> bool:
        """
        Checks if the provided dictionary contains a key named 'func'.

        This function is used to determine whether a given dictionary includes a specific
        key named 'func'.

        :param field: The dictionary to be checked.
        :type field: dict
        :return: Returns True if the dictionary contains the key 'func',
                 otherwise returns False.
        :rtype: bool
        """
        return 'func' in field

    def has_name(self, field: dict) -> bool:
        """
        Checks whether the provided dictionary `field` contains a key named 'name'.

        This method inspects the given dictionary and determines if the key 'name'
        exists within it.

        :param field: The dictionary to be checked for the presence of the 'name' key.
        :type field: dict
        :return: A boolean value indicating whether the dictionary contains a 'name' key.
        :rtype: bool
        """
        return 'name' in field

    def has_function_key(self, field: dict, function_key: str) -> bool:
        """
        Checks if a field contains a specified function key.

        This method determines whether a dictionary representing a field includes
        the provided function key by verifying if the field has a name, is classified
        as a function, and the specified function key is present in the 'func' attribute
        of the field dictionary.

        :param field: A dictionary representing a field.
        :type field: dict
        :param function_key: The function key to check for existence in the field.
        :type function_key: str
        :return: True if the field contains the specified function key, otherwise False.
        :rtype: bool
        """
        return self.has_name(field) and self.is_function(field) and function_key in field[self.FUNCTION_KEY]

    def build_func_field(self, field: dict, func: Callable[[dict], int|str|None|bool|pd.Series|list]) -> DataFrameField:
        """
        Generates a DataFrameField instance, combining the attributes of a provided
        field dictionary along with a user-defined transformation function. This
        method establishes a mapping between field metadata and the applied function for
        data transformation while maintaining essential configuration attributes.

        :param field: A dictionary containing the metadata about the field. Expected
                      keys include 'name', 'field type', and 'cast type'.
        :param func: A callable function that accepts a dictionary as input and returns
                     an output of types int, str, None, bool, or pd.Series. This
                     function is used to perform transformations or computations on the
                     field data.
        :return: A DataFrameField object constructed with metadata and the specified
                 transformation function.
        """

        return DataFrameField(
            name=field[self.NAME_KEY],
            nullable=self.is_nullable(field),
            source_name=None,
            field_type=field[self.FIELD_TYPE_KEY],
            func=func,
            cast_type=field.get(self.CAST_KEY, False) is True
        )

    def get_source_name(self, field: dict) -> str|None:
        """
        Retrieves the source name from the given field dictionary, based on a specified key structure.

        This method is designed to extract the source name by checking whether the
        key defined as SOURCE_NAME_KEY exists within the structure determined by
        FUNCTION_KEY in the provided field dictionary. If the key does not directly
        exist within the initial level of the FUNCTION_KEY, it searches deeper into
        the values of the FUNCTION_KEY to locate the SOURCE_NAME_KEY.

        :param field: The dictionary containing a potential hierarchical structure
            where the source name might be located.
        :type field: dict
        :return: The source name if found, otherwise None.
        :rtype: str | None
        """

        if self.SOURCE_NAME_KEY in field:
           return field[self.SOURCE_NAME_KEY]

        if self.FUNCTION_KEY in field:
            for func in field[self.FUNCTION_KEY].values():
                if func is not None and self.SOURCE_NAME_KEY in func:
                    return func[self.SOURCE_NAME_KEY]

        return None


