import pandas as pd

from .validation_field import ValidationFailure
from .data_frame_configuration import DataFrameConfiguration

class Reporter:
    """
    Handles the process of reporting the state of operations, including the start,
    error occurrences, and conclusion of specific processes. This class is designed
    to ensure consistent and structured reporting based on input configurations and
    provided data. It supports integration with external monitoring and logging tools
    for enhanced observability.
    """

    def report_start(self, file_path: str):
        """
        Reports the start of a process based on the given configuration.

        :return: None
        """
        pass

    def report_error(self, error: Exception):
        """
        Reports an error by capturing the given exception.

        This method is used to handle error reporting processes when an exception occurs.
        It facilitates logging, monitoring, or other specified error handling mechanisms.

        :param error: The exception that needs to be reported.
        :type error: Exception
        :return: None
        """
        pass

    def report_end(self, file_path: str, data: pd.DataFrame):
        """
        Generates a report based on the provided configuration and data at the end of a
        specific processing routine. This function is called to finalize and encapsulate
        all relevant information into a structured format specified by the configuration.

        :param configuration: Contains the configuration settings required for generating
            the report. These settings determine the layout, formatting, filters, and
            other properties used during the reporting process.
        :type configuration: DataFrameConfiguration
        :param data: The input data in the form of a pandas DataFrame upon which the
            report is generated. This data represents the final state to be included in
            the report.
        :type data: pd.DataFrame
        :return: Finalized report data or outcomes (can vary based on implementation).
            Expected to provide a structured representation directly derived from the
            configuration and data inputs.
        :rtype: None
        """
        pass

    def report_output(self, data: pd.DataFrame, output: str):
        """
        Reports the given data to the specified output location. The method processes
        the provided DataFrame and produces output formatted as per the requirements.
        The output could be written to a file, database, or another destination
        determined by the `output` parameter.

        :param data: The data to be processed and reported.
        :type data: pandas.DataFrame
        :param output: The destination where the processed data will be written.
        :type output: str
        :return: None
        :rtype: None
        """
        pass

    def report_configuration(self, configuration: DataFrameConfiguration):
        """
        Reports configuration details for DataFrame-based structures.

        This method is designed to handle and process a given configuration object,
        formatted as an instance of `DataFrameConfiguration`. The configuration
        represents various parameters and settings for managing DataFrame-based
        data structures. Implementation includes scenarios for reporting the
        current configuration state to an external system or logging the details
        internally.

        :param configuration: The configuration object to be reported. Contains
            settings and parameters pertinent to DataFrame configurations.
        :type configuration: DataFrameConfiguration
        :return: None indicates that the operation was successfully executed, with
            no additional data returned.
        :rtype: None
        """
        pass

    def report_debug(self, debug_message: str, data: pd.DataFrame|None = None):
        """
        Logs and reports the provided debug message for analysis or tracking purposes.
        This method facilitates streamlined logging processes by accepting a debug message
        as input.

        :param debug_message: The debug message string provided for logging or reporting purposes.
        :type debug_message: str

        :return: None
        """
        pass

    def report_info(self, message: str):
        """
        Logs an informational message typically used for normal operational messages.

        This method is used to report informational level logs to the system.
        The logged message provides context for operations that were carried
        out successfully or key milestones reached.

        :param message: The informational message to be logged.
        :type message: str
        :return: None
        """
        pass

    def save_validation_failure(self, validation_failure: ValidationFailure):
        """
        Saves a validation failure for further processing.

        This method is responsible for storing an instance of the ValidationFailure
        class for later use. It can be utilized to log, analyze, or handle
        failed validation cases systematically.

        :param validation_failure: An instance of ValidationFailure containing
            details about the failed validation.
        :type validation_failure: ValidationFailure
        """
        pass

    def report_validation_failure(self):
        """
        Reports validation failure encountered during processing.

        This function is typically invoked when a validation check fails
        and the system needs to log or handle the failure accordingly. It
        does not accept any arguments, and its behavior is dictated by the
        implementation within the function.

        :return: None
        """
        pass

class PrintReporter(Reporter):
    """
    A reporter class for printing updates during file processing.

    This class provides a simple implementation of the Reporter
    interface by printing messages about the process status,
    including the start, errors, and completion, to the standard
    output. It is designed for debugging or quick monitoring of
    the file processing and provides instant feedback on the
    processing state.

    :ivar some_attribute: Provide a description of what this attribute
        represents, its role, etc., if applicable to the parent
        Reporter class.
    :type some_attribute: type
    """

    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug
        self.validation_failures: list[ValidationFailure] = []


    def report_start(self, file_path: str):
        print(f"Starting processing for {file_path}")

    def report_error(self, error: Exception):
        print(f"Error processing file: {error}")

    def report_end(self, file_path: str, data: pd.DataFrame):
        print(f"Finished processing for {file_path} - {len(data)} rows")

    def report_configuration(self, configuration: DataFrameConfiguration):
        print(f"Loading configuration for {len(configuration.fields)} fields")
        if self.debug:
            for f in configuration.fields:
                print(f" - {f}")

    def report_debug(self, debug_message: str, data: pd.DataFrame|None = None):
        if self.debug:
            print(f"DEBUG: {debug_message}")

            if data is not None:
                print(data)

    def report_info(self, message: str):
        print(message)

    def save_validation_failure(self, validation_failure: ValidationFailure):
        self.validation_failures.append(validation_failure)

    def report_validation_failure(self):
        print(f"{len(self.validation_failures)} validation failures encountered:")

        for v in self.validation_failures:
            print(f" - {v}")


__reporter: Reporter|None = None

def get_reporter(debug: bool = False, reporter: Reporter|None = None) -> Reporter:
    """
    Get the reporter instance.
    :param debug:
    :return:
    """
    global __reporter

    if reporter is not None:
        __reporter = reporter

    if not isinstance(__reporter, Reporter):
        print("Creating print reporter")
        __reporter = PrintReporter(debug)

    return __reporter

