from io import StringIO

import pandas as pd

from pancham.data_frame_configuration import DataFrameConfiguration
from pancham.data_frame_loader import DataFrameLoader
from pancham.reporter import get_reporter
from .salesforce_connection import get_connection
from pancham.output_configuration import OutputConfiguration, OutputWriter

SALESFORCE_CSV_BULK = 'salesforce_csv_bulk'


class SalesforceCsvBulkOutputConfiguration(OutputConfiguration):

    def can_apply(self, configuration: dict):
        """
        Determines whether the Salesforce Bulk configuration can be applied
        based on the presence and validity of required keys.

        :param configuration: A dictionary containing the configuration details.
        :type configuration: dict
        :return: A boolean indicating whether the configuration is valid
                 and can be applied.
        :rtype: bool
        :raises ValueError: If the Salesforce Bulk configuration is present
                            but missing the 'object_name' key.
        """
        salesforce_configuration = self.extract_configuration_by_key(configuration, SALESFORCE_CSV_BULK)

        if salesforce_configuration is None:
            return False

        if 'csv_file' not in salesforce_configuration:
            raise ValueError('SalesforceBulkOutput requires an object_name')

        return True

    def to_output_writer(self, configuration: dict) -> OutputWriter:
        """
        Get output writer
        :param configuration:
        :return:
        """
        salesforce_configuration = self.extract_configuration_by_key(configuration, SALESFORCE_CSV_BULK)

        return SalesforceCsvBulkOutputWriter(salesforce_configuration)

class SalesforceCsvBulkOutputWriter(OutputWriter):
    """
    Load the bulk api with an existing csv file
    """

    def __init__(
            self,
            configuration: dict
            ):
        super().__init__(configuration)
        self.csv_file = configuration.get('csv_file')
        self.object_name = configuration.get('object_name')
        self.method = configuration.get('method', 'insert')


    def write(self,
              data: pd.DataFrame,
              success_handler: DataFrameConfiguration | None = None,
              failure_handler: DataFrameConfiguration | None = None,
              loader: DataFrameLoader | None = None
              ):
        """
        Writes data to a Salesforce object using the Salesforce Bulk API 2.0. The method
        uses the provided configuration to determine the object name and how to handle
        successful and failed records. Data is processed in bulk and relevant handlers
        are invoked for success and failure cases.

        The data provided is first converted into a list of dictionaries representing records.
        The function then interacts with the Salesforce client, performing batch insert
        operations. After submission, success and failure handlers are employed (if configured)
        to process the resulting records.

        :param data: The data to be inserted into the Salesforce object. It is expected
            to be in the form of a pandas DataFrame.
        :type data: pd.DataFrame
        :param configuration: A dictionary containing configuration details. Must include
            the key "object_name" to specify the target Salesforce object. Additionally, keys
            for "success_handler" and "failure_handler" may define processing behaviors for
            successful and failed records.
        :type configuration: dict
        :return: None
        """
        sf = get_connection()
        reporter = get_reporter()

        reporter.report_debug(f'Writing to Salesforce Bulk', self.csv_file)

        if self.method == 'upsert':
            results = getattr(sf.bulk2, self.object_name).upsert(self.csv_file)
        elif self.method == 'update':
            results = getattr(sf.bulk2, self.object_name).update(self.csv_file)
        else:
            results = getattr(sf.bulk2, self.object_name).insert(self.csv_file)

        for r in results:
            job_id = r['job_id']

            reporter.report_debug(f'Salesforce Bulk job {job_id} completed', r)
            reporter.report_debug(f'Applying success and failure handlers {success_handler}, {failure_handler}')

            if success_handler is not None:
                success = getattr(sf.bulk2, self.object_name).get_successful_records(job_id)
                reporter.report_debug('success', success)
                self.__save_handled_data(success, success_handler, loader)

            if failure_handler is not None:
                failed = getattr(sf.bulk2, self.object_name).get_failed_records(job_id)
                reporter.report_debug('failures', failed)
                self.__save_handled_data(failed, failure_handler, loader)


    def __save_handled_data(self, data: str, handler_configuration: DataFrameConfiguration, loader: DataFrameLoader):
        """
        Handles the saving of processed data using a configured output writer.

        This method reads data in CSV format, processes it into a pandas DataFrame, and
        writes the result using the provided output writer instance. The handler
        configuration must include the instance of an OutputWriter to determine how
        and where the data is saved.

        :param data: The string containing CSV formatted data to be handled and saved.
        :type data: str
        :param handler_configuration: A dictionary containing the configuration for the
            output writer. Must include the key 'instance' associated with an
            OutputWriter object.
        :type handler_configuration: dict
        :return: None
        """
        handler: OutputWriter = handler_configuration.output[0].primary_writer

        df = pd.read_csv(StringIO(data))
        processed = loader.process_dataframe(df, handler_configuration)
        handler.write(processed, handler_configuration)

