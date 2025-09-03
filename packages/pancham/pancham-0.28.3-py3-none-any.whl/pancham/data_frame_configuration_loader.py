import yaml
from typing import Literal

from .validation_field import ValidationField, ValidationRule
from .data_frame_configuration import MergeConfiguration
from .configuration.field_parser import FieldParser
from .data_frame_configuration import DataFrameConfiguration
from .output_configuration import OutputConfiguration, OutputActivitySet


class DataFrameConfigurationLoader:

    def __init__(self, field_parsers: list[FieldParser], output_configuration: list[OutputConfiguration]):
        self.field_parsers = field_parsers
        self.output_configuration = output_configuration

    def load(self, filename: str) -> DataFrameConfiguration:

        data = self.load_file(filename)

        self.__validate_input(data, filename)

        sheet: str|None = self.__get_configuration_for_file_type(data, 'sheet', ['xlsx'])
        key: str|None = self.__get_configuration_for_file_type(data, 'key', ['json', 'yaml'])
        configuration = self.__load_section(data, "main", sheet=sheet, key=key)

        self.__load_additional_fields(data, configuration, 'pre')
        self.__load_additional_fields(data, configuration, 'post')
        self.__load_additional_fields(data, configuration, 'validation')

        configuration.drop_duplicates = data.get('drop_duplicates', None)
        configuration.process = data.get('process', 'parse')

        if data.get('use_iterator', False) is True:
            configuration.use_iterator = True
            configuration.chunk_size = data.get('chunk_size', 100000)

        return configuration

    def load_file(self, filename: str) -> dict:
        """
        Loads the content of a given file and returns the data as a dictionary. The file
        is typically expected to contain structured data in a format such as JSON or YAML.

        :param filename: Name of the file to be loaded. The file should exist at the
            specified path and must be readable.
        :type filename: str

        :return: A dictionary containing the data loaded from the file.
        :rtype: dict
        """
        pass

    def __validate_input(self, data: dict, filename: str):
        """
        Validate the configuration has the keys that it needs

        If the input is not valid throw a value error
        """
        if ("file_path" not in data or "file_type" not in data) and "query" not in data:
            raise ValueError(f"file_path and file_type are required fields in {filename}")
        
    def __get_configuration_for_file_type(self, data: dict, key: str, types: list[str]) -> str|None:
        """
        Test if the file type matches the expected value and return the key if it exists
        """
        if data["file_type"] in types and key in data:
            return data[key]
        
        return None
    
    def __load_additional_fields(self, data: dict, configuration: DataFrameConfiguration, key: Literal['pre', 'post', 'validation']):
        """
        Load the keys for the additional items
        """
        if key in data:
            for d in data[key]:
                if key == 'pre':
                    configuration.pre_run_configuration.append(self.__load_section(d, d['name']))
                if key == 'post':
                    configuration.post_run_configuration.append(self.__load_section(d, d['name']))
                if key == 'validation':
                    configuration.validation_rules.append(self.__load_validation_configuration(d))

    def __load_section(self, data: dict, label: str, sheet: str|None = None, key: str|None = None) -> DataFrameConfiguration:
        """
        Dataframes are loaded in sections, allowing the pre and post steps to be their own configuration that
        is loaded using the same methods

        :param data: A dictionary containing configuration data needed for defining the DataFrame
            and its associated fields. Must include a "file_path" and "file_type" for "main" label or
            nested label-specific details when not "main".
        :type data: dict
        :param label: A string indicating the label for the section to process. Allows identifying
            the required part of the input data.
        :type label: str
        :param sheet: Optional sheet identifier for file-based input if relevant (e.g., Excel files).
            Determines a particular sheet to pull data from when parsing input.
        :type sheet: str | None
        :return: A configured `DataFrameConfiguration` object instantiated based on input_data and label,
            populated with fields parsed by supported parsers, and associated output configurations if specified
            and applicable.
        :rtype: DataFrameConfiguration
        :raises ValueError: If a field in the input data cannot be parsed by any available field parser.
        """
        configuration = self.__load_base_configuration(data, label, sheet=sheet, key=key)

        if configuration.name.startswith('test'):
            return configuration

        configuration = self.__parse_fields(configuration, data)

        if 'output' in data:
            for c in self.output_configuration:
                if c.can_apply(data):
                    output_writer = c.to_output_writer(data)
                    success_handler = self.__parse_post_output(output_writer.root_configuration.get('success_handler', None))
                    failure_handler = self.__parse_post_output(output_writer.root_configuration.get('failure_handler', None))

                    configuration.add_output(OutputActivitySet(primary_writer=output_writer, success_handler=success_handler, failure_handler=failure_handler))

        return configuration

    def __load_base_configuration(self, data: dict, label: str, sheet: str|None = None, key: str|None = None) -> DataFrameConfiguration:
        """
        Load the base configuration for a DataFrame. Depending on the label, it initializes
        the appropriate DataFrameConfiguration object using the passed parameters. When
        the label is 'main', it utilizes the file-related data for configuration; for other
        labels, it evaluates additional merge configurations if provided.

        :param data: A dictionary containing input data configuration. It may include keys
                     like 'file_path', 'file_type', 'name', and 'depends_on' for defining
                     the DataFrame structure, as well as an optional 'merge' key which must
                     contain sub-keys if merge configuration is required.
        :param label: A string identifying the label of the configuration. It dictates
                      the configuration behavior, particularly whether merge configurations
                      are applicable or not.
        :param sheet: An optional string denoting the sheet name for configurations related
                      to spreadsheet files.
        :param key: An optional string representing the unique key identifier relevant to
                    the configuration.
        :return: A DataFrameConfiguration object initialized based on the provided
                 configuration data and label.
        """
        if label == 'main':
            return DataFrameConfiguration(data.get("file_path", ''), data.get("file_type", ''), name=data['name'], sheet=sheet, key=key, depends_on=data.get('depends_on', None), query=data.get('query', None))

        merge_configuration = None
        if 'merge' in data:
            merge_dict = data['merge']
            merge_configuration = MergeConfiguration(merge_dict.get('type', 'processed'), merge_dict.get('source_key', None), merge_dict.get('processed_key', None))
        return DataFrameConfiguration(label, label, name=data['name'], merge_configuration=merge_configuration)

    def __load_validation_configuration(self, data: dict) -> ValidationField:
        """
        Loads and processes a validation configuration from the provided data dictionary. The function
        parses the validation configuration structure, extracts relevant information, and maps it
        into corresponding configuration objects such as validation rules and validation fields.
        The resulting object encapsulates all validation details for further consumption.

        :param data: A dictionary containing validation configuration details. Expected keys include
            'name', 'file_type', 'file_path', 'key', 'sheet', and 'rules'.
        :type data: dict

        :return: A `ValidationField` object configured with the provided validation rules and details.
        :rtype: ValidationField
        """
        rule: ValidationRule|None = None

        if 'rule' in data:
            rule_config = data['rule']
            rule = ValidationRule(rule_config['test_field'], rule_config.get('id_field', None), rule_config.get('properties', {}))

        return ValidationField(
            name = data['name'],
            rule=rule
        )

    def __parse_fields(self, configuration: DataFrameConfiguration, data: dict) -> DataFrameConfiguration:
        """
        Parses fields from the provided data based on the configuration and applicable
        field parsers. If a field cannot be parsed by any parser, an exception is raised.
        The function iterates through the 'fields' provided in the input data and attempts
        to parse each using the available field parsers.

        :param configuration: The DataFrameConfiguration object that will be updated
            with parsed fields.
        :param data: A dictionary containing field definitions under the 'fields' key
            for parsing.
        :return: The updated DataFrameConfiguration object containing the successfully
            parsed fields.
        :rtype: DataFrameConfiguration
        :raises ValueError: If a field in the data cannot be parsed by any of the
            available field parsers.
        """
        if 'fields' in data:
            for f in data['fields']:
                has_parsed = False
                for parser in self.field_parsers:
                    if parser.can_parse_field(f):
                        field = parser.parse_field(f)

                        if 'supress_error' in f:
                            field.supress_error = f['supress_error']

                        configuration.add_field(data_frame_field=field)
                        has_parsed = True
                        break

                if not has_parsed:
                    raise ValueError(f"Could not parse field {f}")

        return configuration

    def __parse_post_output(self, configuration: dict|None) -> DataFrameConfiguration|None:
        """
        Get configuration for handlers
        :param configuration:
        :param handler:
        :return:
        """

        if configuration is None:
           return None

        dataframe_configuration = self.__parse_fields(DataFrameConfiguration(file_path='', file_type='', name=''), configuration)

        for c in self.output_configuration:
            if c.can_apply(configuration):
                output_writer = c.to_output_writer(configuration)
                dataframe_configuration.add_output(OutputActivitySet(primary_writer=output_writer, success_handler=None, failure_handler=None))

                return dataframe_configuration

        return None




class YamlDataFrameConfigurationLoader(DataFrameConfigurationLoader):

    def load_file(self, filename: str) -> dict:
        """
        Loads data from a YAML file and returns it as a dictionary.

        The method attempts to open the specified file in read mode and parse its
        content using the YAML-safe loader. The retrieved data is then returned to
        the caller as a dictionary.

        :param filename: The name of the YAML file to load.
        :type filename: str

        :return: A dictionary containing the parsed YAML file data.
        :rtype: dict
        """
        with open(filename, 'r') as file:
            return yaml.safe_load(file)