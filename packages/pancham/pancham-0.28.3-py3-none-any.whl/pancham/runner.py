from typing import Optional

import pandas as pd

from .validation import ContainsValidation, MatchingValidation, NotAllNullValidation, NotNullValidation, OneOfValidation
from .validation_field import ValidationStep, ValidationInput
from .configuration.database_match_field_parser import DatabaseMatchFieldParser
from .configuration import DynamicFieldParser, DateTimeFieldParser, RemoveFieldParser, RegexExtractFieldParser, ToBoolFieldParser, SFLookupFieldParser, FillNanFieldParser, DatabaseFixedFieldParser, DatabaseMultiFieldSearchParser, StaticFieldParser, ToIntFieldParser, FieldParser, MatchFieldParser, SplitFieldParser, PartTextExtractorParser, ConcatFieldParser, TextFieldParser, EmailRegexMatchParser, RegexMatchFieldParser, NumberFormatFieldParser
from .configuration.explode_field_parser import ExplodeFieldParser
from .configuration.deduplicate_field_parser import DeduplicateFieldParser
from .data_frame_configuration import DataFrameConfiguration
from .data_frame_loader import DataFrameLoader
from .data_frame_configuration_loader import YamlDataFrameConfigurationLoader
from .database.database_engine import initialize_db_engine
from .database.sql_file_loader import SqlFileLoader, SqlExecuteFileLoader
from .database.database_output import DatabaseOutput
from .file_loader import FileLoader, ExcelFileLoader, YamlFileLoader, CsvFileLoader, JsonFileLoader
from .output_configuration import OutputWriter, OutputConfiguration
from .pancham_configuration import PanchamConfiguration, OrderedPanchamConfiguration
from .reporter import Reporter, PrintReporter, get_reporter
from .integration import SalesforceBulkOutputConfiguration, SalesforceCsvBulkOutputConfiguration
from .integration.salesforce_query_loader import SalesforceQueryLoader

DEFAULT_LOADERS = {
    'xlsx': ExcelFileLoader(),
    'sql_file': SqlFileLoader(),
    'sql_execute': SqlExecuteFileLoader(),
    'yaml': YamlFileLoader(),
    'csv': CsvFileLoader(),
    'json': JsonFileLoader(),
    'soql': SalesforceQueryLoader()
}
DEFAULT_REPORTER = PrintReporter()

DEFAULT_FIELD_PARSERS = [
    TextFieldParser(),
    MatchFieldParser(),
    DateTimeFieldParser(),
    DynamicFieldParser(),
    ToIntFieldParser(),
    PartTextExtractorParser(),
    StaticFieldParser(),
    DatabaseMatchFieldParser(),
    DatabaseFixedFieldParser(),
    SplitFieldParser(),
    ExplodeFieldParser(),
    ConcatFieldParser(),
    DatabaseMultiFieldSearchParser(),
    RemoveFieldParser(),
    DeduplicateFieldParser(),
    RegexMatchFieldParser(),
    RegexExtractFieldParser(),
    EmailRegexMatchParser(),
    SFLookupFieldParser(),
    FillNanFieldParser(),
    ToBoolFieldParser(),
    NumberFormatFieldParser()
]
DEFAULT_OUTPUTS = [
    DatabaseOutput(),
    SalesforceBulkOutputConfiguration(),
    SalesforceCsvBulkOutputConfiguration()
]
DEFAULT_VALIDATION_RULES = [
    NotNullValidation(),
    OneOfValidation(),
    NotAllNullValidation(),
    MatchingValidation(),
    ContainsValidation()
]

def start_pancham(
        configuration: str,
        data_configuration: Optional[str],
        test: bool = False
):
    print("Starting Pancham!")
    pancham_configuration = OrderedPanchamConfiguration(configuration)

    reporter = get_reporter(pancham_configuration.debug_status)

    print(f"Reporter enabled - Debug = {pancham_configuration.debug_status}")
    runner = PanchamRunner(pancham_configuration, reporter = reporter)

    if data_configuration is not None:
        runner.load_and_run(data_configuration)
    else:
        if test:
            runner.run_all_tests()
        else:
            runner.run_all()



class PanchamRunner:

    def __init__(self,
                 pancham_configuration: PanchamConfiguration,
                 file_loaders: dict[str, FileLoader] | None = None,
                 reporter: Reporter | None = None,
                 field_parsers: list[FieldParser] | None = None,
                 outputs_configuration: list[OutputConfiguration] | None = None,
                 validation_rules: list[ValidationStep] | None = None
                ):
        self.pancham_configuration = pancham_configuration
        self.loaded_outputs: dict[str, OutputWriter] = {}

        if file_loaders is None:
            self.file_loaders = DEFAULT_LOADERS
        else:
            self.file_loaders = file_loaders

        if reporter is None:
            self.reporter = DEFAULT_REPORTER
        else:
            self.reporter = reporter

        if field_parsers is None:
            self.field_parsers = DEFAULT_FIELD_PARSERS
        else:
            self.field_parsers = field_parsers

        if outputs_configuration is None:
            self.outputs_configuration = DEFAULT_OUTPUTS
        else:
            self.outputs_configuration = outputs_configuration

        if validation_rules is None:
            self.validation_rules = DEFAULT_VALIDATION_RULES
        else:
            self.validation_rules = validation_rules

        self.loader = DataFrameLoader(self.file_loaders, self.reporter, self.pancham_configuration)

    def run_all(self):
        """
        Executes the primary function for processing all specified configurations.

        Summary:
        This method orchestrates the loading of configuration files, reporting their
        details, and executing an operation based on the loaded configuration. The
        process leverages a `YamlDataFrameConfigurationLoader` to parse and transform
        YAML-based configurations into usable formats. Each configuration file is
        subsequently passed to a reporter for documentation purposes, and then
        handled via the `run()` method.

        :param self: Represents the instance of the class.
        :raises Exception: An error raised if any configuration file fails to load
            or process accordingly.
        :return: None
        """
        configuration_loader = YamlDataFrameConfigurationLoader(field_parsers=self.field_parsers, output_configuration=self.outputs_configuration)
        loaders = list(map(lambda f: configuration_loader.load(f), self.pancham_configuration.mapping_files))

        for l in loaders:
            self.reporter.report_configuration(l)
            self.run(l)
            self.run_validation(l)

        self.reporter.report_validation_failure()

    def run_all_tests(self):
        """
        Executes all tests by loading configuration data from YAML files,
        validating the data, and then reporting the validation failures.

        :raises ValidationError: If validation fails for any of the configurations.
        :raises ConfigurationLoadError: If there is an error in loading the YAML configuration.
        :raises ReportError: If there is an issue generating the validation failure report.
        :return: None
        """
        configuration_loader = YamlDataFrameConfigurationLoader(field_parsers=self.field_parsers, output_configuration=self.outputs_configuration)
        loaders = list(map(lambda f: configuration_loader.load(f), self.pancham_configuration.test_files))

        for l in loaders:
            self.run_validation(l)

        self.reporter.report_validation_failure()

    def load_and_run(self, configuration_file: str):
        configuration_loader = YamlDataFrameConfigurationLoader(field_parsers=self.field_parsers, output_configuration=self.outputs_configuration)
        configuration = configuration_loader.load(configuration_file)

        self.reporter.report_configuration(configuration)

        self.run(configuration)
        self.run_validation(configuration)
        self.reporter.report_validation_failure()

    def run(self, configuration: DataFrameConfiguration):
        """
        Executes the data loading and writing process based on the provided configuration.

        The method initializes a DataFrameLoader with the given file loaders and
        reporter, then uses it to load data as specified in the input configuration.
        Once the data is loaded, it iterates over the output specifications defined
        in the configuration and writes the data to each output destination by obtaining
        the appropriate writer.

        :param configuration: Configuration object defining how the data will be
            loaded and written. This includes input details for loading the data
            and output specifications for writing the data.
        :type configuration: DataFrameConfiguration

        :return: None
        """
        initialize_db_engine(self.pancham_configuration, self.reporter)
        if configuration.name.startswith('test'):
            return

        self.reporter.report_info(f"Starting run for {configuration.name}")

        for data in self.loader.load(configuration):
            self.reporter.report_debug(f'Writing data {len(data.processed)}')
            self.__write_output(configuration, data.processed, self.loader)

            for post_run_configuration in configuration.post_run_configuration:
                input_data = data.get_required_dataframe(post_run_configuration.merge_configuration)
                post_run_data = self.loader.process_dataframe(input_data, post_run_configuration)

                self.__write_output(post_run_configuration, post_run_data, self.loader)

    def run_validation(self, configuration: DataFrameConfiguration):
        """
        Executes validation checks on a given data configuration based on predefined
        validation rules. This function processes each validation rule within the
        provided configuration, loads the corresponding file data for each validation
        set, and runs validations to identify failures that are subsequently reported.

        :param configuration: Validation configuration containing the rules to check
            and the associated data requirements.
        :type configuration: DataFrameConfiguration
        :return: None
        """
        initialize_db_engine(self.pancham_configuration, self.reporter)

        for data in self.loader.load_file(configuration):

            # Loop the validation objects in the configuration
            for validation in configuration.validation_rules:

                # Loop the available rules to find one we can apply to this
                for loaded_rule in self.validation_rules:

                    # If the rule names matches, then execute it
                    if loaded_rule.get_name() == validation.name:
                        validation_input = ValidationInput(validation.name, data, validation.rule)
                        failures = loaded_rule.validate(validation_input)

                        for failure in failures:
                            self.reporter.save_validation_failure(failure)

    def __write_output(self, configuration: DataFrameConfiguration, output: pd.DataFrame, loader: DataFrameLoader):
        """
        Writes the given output DataFrame to the destinations specified in the
        configuration's output writers.

        Iterates through each output writer defined in the input configuration
        and delegates the writing of the provided DataFrame to the respective
        writer.

        :param configuration: Configuration object containing a list of output
            writers that specify the destinations for writing the DataFrame.
        :type configuration: DataFrameConfiguration
        :param output: The DataFrame to be written to the specified destinations.
        :type output: pd.DataFrame
        :return: None
        """
        for output_writer in configuration.output:
            output_writer.primary_writer.write(
                output,
                success_handler=output_writer.success_handler,
                failure_handler=output_writer.failure_handler,
                loader=loader
            )

