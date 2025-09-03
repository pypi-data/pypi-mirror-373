import pandas as pd

from pancham.data_frame_configuration import DataFrameConfiguration
from pancham.data_frame_loader import DataFrameLoader
from .database_engine import get_db_engine
from pancham.output_configuration import OutputConfiguration, OutputWriter
from pancham.reporter import get_reporter

class DatabaseOutput(OutputConfiguration):

    def can_apply(self, configuration: dict):
        """
        Determines whether the provided configuration can be applied.

        This method validates if the configuration contains the necessary output
        settings for a database and ensures that all required fields are present.

        :param configuration: The configuration dictionary to validate.
                              It should include an 'output' key with a list of
                              output configurations.
        :type configuration: dict
        :return: Indicates whether the configuration can be applied.
        :rtype: bool
        :raises ValueError: If the 'database' output type is detected but the
                            required 'table' key is missing.
        """
        database_configuration = self.extract_configuration_by_key(configuration, 'database')

        if database_configuration is None:
            return False

        if 'table' not in database_configuration:
            raise ValueError('table is required in database output configuration')

        return True

    def to_output_writer(self, configuration: dict) -> OutputWriter:
        database_config = self.extract_configuration_by_key(configuration, 'database')
        return DatabaseOutputWriter(database_config)


class DatabaseOutputWriter(OutputWriter):

    def __init__(
            self,
            configuration: dict
    ):
        super().__init__(configuration)
        self.table = configuration['table']
        self.columns = configuration.get('columns', [])
        self.merge_key = configuration.get('merge_key', None)
        self.on_missing = configuration.get('on_missing', None)
        self.merge_data_type = configuration.get('merge_data_type', None)
        self.native = configuration.get('native', None)

    def write(self,
              data: pd.DataFrame,
              success_handler: DataFrameConfiguration | None = None,
              failure_handler: DataFrameConfiguration | None = None,
              loader: DataFrameLoader | None = None
              ):
        """
        Write data from a pandas DataFrame to a database table using the specified
        configuration. The function optionally filters the DataFrame columns
        based on a list of column names provided in the configuration.

        :param data: A pandas DataFrame representing the data to be written
            to the database.
        :type data: pandas.DataFrame
        :param configuration: A dictionary containing configuration details
            for writing the DataFrame. Possible keys include:
            - "columns": List of column names to filter the DataFrame.
            - "table": Name of the destination database table.
        :type configuration: dict
        :return: None
        """
        reporter = get_reporter()
        reporter.report_debug(f'Writing to database', data)

        if len(self.columns) > 0:
            data = data[self.columns]

        if self.merge_key is not None:
            for _, row in data.iterrows():
                get_db_engine().merge_row(row, self.table, self.merge_key, self.on_missing, self.merge_data_type, self.native)
            return

        get_db_engine().write_df(data, self.table)
