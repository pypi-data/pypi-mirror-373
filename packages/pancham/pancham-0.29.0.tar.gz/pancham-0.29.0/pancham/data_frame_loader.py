from typing import Iterator

import numpy as np
import pandas as pd
import dask.dataframe as dd
from pandera.errors import SchemaError

from .file_loader_configuration import FileLoaderConfiguration
from .data_frame_configuration import MergeConfiguration
from .pancham_configuration import PanchamConfiguration
from .data_frame_configuration import DataFrameConfiguration
from .file_loader import FileLoader
from .reporter import Reporter

class DataFrameOutput:
    """
    Represents a container for storing and handling data in a source and
    processed format using pandas DataFrames.

    This class is designed to manage two pandas DataFrames: one as the
    original dataset (source) and another that represents the dataset after
    being processed (processed). Its purpose is to provide an organized
    structure for handling data transformation workflows.

    :ivar source: The original pandas DataFrame containing raw data before
        processing.
    :type source: pd.DataFrame
    :ivar processed: The pandas DataFrame containing the data after being
        processed.
    :type processed: pd.DataFrame
    """

    MAX_ROWS_IN_FRAME = 25000

    def __init__(self, source: pd.DataFrame, processed: pd.DataFrame):
        self.source = source
        self.processed = processed

    def get_required_dataframe(self, merge_configuration: MergeConfiguration) -> pd.DataFrame:
        """
        Determines and retrieves the required DataFrame based on the specified
        merge configuration. The function decides which DataFrame to return or
        handle merging logic accordingly.

        If the `merge_configuration` is None, it returns a copy of the
        `processed` DataFrame. When the `required_dataframe` attribute is
        'source', a copy of the `source` DataFrame is returned. If
        `required_dataframe` is 'merged', and both `processed_key` and
        `source_key` are provided, the function performs a left merge
        operation between `source` and `processed` DataFrames. Otherwise,
        it defaults to returning a copy of the `processed` DataFrame.

        :param merge_configuration: Configuration object specifying which
            DataFrame to return or how to merge existing ones
        :type merge_configuration: MergeConfiguration
        :return: The resolved DataFrame based on the conditions provided in
            merge_configuration
        :rtype: pd.DataFrame
        """
        if merge_configuration is None:
            return self.processed.copy()

        if merge_configuration.required_dataframe == 'source':
            return self.source.copy()

        if merge_configuration.required_dataframe == 'merged' and merge_configuration.processed_key is not None and merge_configuration.source_key is not None:
            return self.source.merge(self.processed, how='left', left_on=merge_configuration.source_key, right_on=merge_configuration.processed_key)

        return self.processed.copy()

class DataFrameLoader:
    """
    A loader class designed to handle file operations and manipulate dataframes.

    This class provides functionality to load and transform data from various file types
    using specific configurations. It works with customizable file loaders, and includes
    error handling, data validation, and dynamic field computation for producing properly
    structured output.

    :ivar file_loaders: A dictionary mapping file types to their corresponding file
        loader instances. Used to delegate file reading based on the type.
    :type file_loaders: dict[str, FileLoader]
    :ivar reporter: Responsible for reporting the status of the loading process, including
        progress, errors, and other notifications.
    :type reporter: Reporter
    :ivar pancham_configuration: Optional configuration specific to the "Pancham"
        system. If provided, it is used for additional customization of the loading process.
    :type pancham_configuration: PanchamConfiguration | None
    """

    def __init__(self, file_loaders: dict[str, FileLoader], reporter: Reporter, pancham_configuration: PanchamConfiguration|None = None) -> None:
        self.file_loaders = file_loaders
        self.reporter = reporter
        self.pancham_configuration = pancham_configuration

    def load(
            self,
            configuration: DataFrameConfiguration
    ) -> Iterator[DataFrameOutput]:
        """
        Loads and processes data as per the given configuration.

        The function utilizes a given configuration to load a data file, apply necessary renaming
        of columns, process dynamic fields, handle errors, cast columns to specified types,
        and validate the resulting dataset against a predefined schema. It replaces `nan`
        and `-inf` values with 0. After performing all operations, the processed DataFrame
        is returned.

        :param configuration: A data frame configuration object that contains all the necessary settings
                              such as renames, dynamic fields, output fields, cast values,
                              and a validation schema.
        :type configuration: DataFrameConfiguration
        :return: A fully processed and validated pandas DataFrame.
        :rtype: pd.DataFrame
        """
        self.reporter.report_debug("Starting load")
        for source_df in self.load_file(configuration):
            if configuration.drop_duplicates is None:
                prepared_df = source_df.copy()
            else:
                prepared_df = source_df.drop_duplicates(subset=configuration.drop_duplicates)

            processed = self.process_dataframe(prepared_df, configuration)
            yield DataFrameOutput(source_df, processed)

    def process_dataframe(self, source_df: pd.DataFrame, configuration: DataFrameConfiguration) -> pd.DataFrame:
        """
        Processes a Pandas DataFrame based on a set of configuration rules.

        This method takes a source DataFrame and applies a series of transformations
        outlined in the given configuration. These transformations include renaming
        columns, applying dynamic field functions, handling suppressed errors during
        field processing, filtering specific output fields, casting data types, and
        validating the resulting output schema. The result is a processed DataFrame
        suitable for further analysis or usage.

        :param source_df: The source DataFrame to be processed.
        :param configuration: An instance of `DataFrameConfiguration` containing
            renaming instructions, dynamic field definitions, output field filters,
            type casting rules, and schema validation settings.
        :return: A transformed DataFrame adhering to the configuration rules.
        :rtype: pd.DataFrame
        """
        if configuration.process == 'passthrough':
            return source_df.copy()

        split_df = self.__split_df(source_df)

        renamed_df = split_df.rename(columns=configuration.renames)

        for field in configuration.dynamic_fields:
            self.reporter.report_debug(f"Processing dynamic field {field.name} - Data frame field {field.has_df_func()}")
            try:
                if field.has_df_func():
                    renamed_df = field.df_func(renamed_df)
                else:
                    if isinstance(renamed_df, dd.DataFrame):
                        type = configuration.get_field_type(field.name)
                        renamed_df[field.name] = renamed_df.apply(field.func, axis=1, meta=(field.name, type))
                    else:
                        renamed_df[field.name] = renamed_df.apply(field.func, axis=1)
            except Exception as e:
                if field.suppress_errors:
                    self.reporter.report_error(e)
                else:
                    raise e

        if configuration.process == 'append':
            return renamed_df.copy()

        output = renamed_df[configuration.output_fields].copy()

        for key, value in configuration.cast_values.items():
            if value == 'int':
                output[key] = output[key].replace([np.nan, np.inf, -np.inf], 0)
            output[key] = output[key].astype(value)

        if isinstance(output, dd.DataFrame):
            procesed = output.compute()
        else:
            procesed = output

        self.__validate_schema(procesed, configuration)

        return procesed

    def load_file(self, configuration: FileLoaderConfiguration) -> Iterator[pd.DataFrame]:
        """
        Loads a data file based on its specified file type and associated configuration details
        using a corresponding file loader.

        This method determines the appropriate loader for the specified file type as configured
        in the `file_loaders` dictionary. If the file type is not supported, a `ValueError` is
        raised. The appropriate loader's `read_file_from_configuration` method is then invoked to
        load the file, leveraging the configuration provided.

        :param configuration: Configuration object containing details necessary to identify
            and load the file, including file type and related properties.
        :type configuration: DataFrameConfiguration
        :return: A pandas DataFrame object representing the loaded data.
        :rtype: Iterator of pd.DataFrame
        :raises ValueError: If the specified file type is not supported within `file_loaders`.
        """

        file_type = configuration.file_type

        if file_type not in self.file_loaders:
            raise ValueError(f'Unsupported file type: {file_type}')

        loader = self.file_loaders[file_type]

        yield from loader.read_file_from_configuration(configuration, self.pancham_configuration)

    def __validate_schema(self, output: pd.DataFrame, configuration: DataFrameConfiguration):
        """
        Validates the schema of the provided DataFrame against the defined configuration schema.

        This method uses the schema defined in the provided configuration object to validate
        the structure and content of the output DataFrame. If schema validation fails and
        schema validation is not disabled, it raises an error. Otherwise, it logs the issue
        as per the existing configuration.

        :param output: The DataFrame to be validated
        :type output: pd.DataFrame
        :param configuration: Configuration object containing the schema definition for validation
        :type configuration: DataFrameConfiguration
        :return: None
        """
        try:
            configuration.schema.validate(output)
        except SchemaError as e:
            if self.pancham_configuration is not None and self.pancham_configuration.disable_schema_validation:
                self.reporter.report_debug(f'Schema validation failed but is disabled: {e}')
            else:
                raise e

    def __split_df(self, df: pd.DataFrame) -> pd.DataFrame | dd.DataFrame:
        """
        Splits the given DataFrame into smaller partitions if it exceeds the maximum
        number of rows allowed for a single frame. This helps to handle large
        datasets by creating a Dask DataFrame with multiple partitions.

        :param df: Input DataFrame to be split, which can be a pandas DataFrame.
        :type df: pd.DataFrame
        :return: Returns the original DataFrame if the number of rows is within the
            allowed limit. Otherwise, returns a Dask DataFrame partitioned into
            8 segments.
        :rtype: pd.DataFrame | dd.DataFrame
        """
        if self.pancham_configuration is not None and self.pancham_configuration.has_feature_enabled('dask'):
            rows = len(df.index)

            if rows <= DataFrameOutput.MAX_ROWS_IN_FRAME:
                return df

            return dd.from_pandas(df, npartitions=8)

        return df
