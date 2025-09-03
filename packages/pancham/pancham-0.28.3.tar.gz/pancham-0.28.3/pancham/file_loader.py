import json
from typing import Iterator

import pandas as pd
import yaml
from jsonstraw import read_json_chunk

from .file_loader_configuration import FileLoaderConfiguration
from .reporter import get_reporter
from .pancham_configuration import PanchamConfiguration
from .data_frame_configuration import DataFrameConfiguration


class FileLoader:
    """
    Handles the process of loading and reading files.

    A FileLoader should be able to read a file and return a DataFrame. Each child class will
    handle a type of file
    """

    def read_file_from_configuration(self, configuration: FileLoaderConfiguration, pancham_configuration: PanchamConfiguration | None = None) -> Iterator[pd.DataFrame]:
        """
        Reads and processes a file based on the given configuration.

        This method uses the provided configuration to locate and process the
        file accordingly. It expects the configuration object to provide all
        the necessary details such as file path, format, and other processing
        instructions.

        :param pancham_configuration:
        :param configuration: Configuration object containing the details needed
            to locate and process the file.
        :type configuration: DataFrameConfiguration
        :return: A pandas DataFrame containing the data from the file.
        :rtype: pd.DataFrame
        """
        reporter = get_reporter()
        data = []
        will_use_iterator = configuration.use_iterator is True and self.can_yield(configuration)

        if configuration.query is not None:
            """
            If a query is coded into the mapping then load it directly 
            """
            yield self.read_file(configuration.query, query=configuration.query)
            return

        for file_path in self.reduce_file_paths(configuration, pancham_configuration):
            sheet = configuration.sheet
            key = configuration.key
            path = file_path

            if type(file_path) is dict:
                path = file_path['path']
                sheet = file_path.get('sheet', None)
                key = file_path.get('key', None)

            reporter.report_start(path)

            if will_use_iterator:
                yield from self.yield_file(path, sheet = sheet, key = key, chunk_size = configuration.chunk_size)
            else:
                frame = self.read_file(path, sheet = sheet, key = key)
                data.append(frame)
                reporter.report_end(path, frame)

        if not will_use_iterator:
            data = pd.concat(data)
            yield data

    def read_file(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Reads data from the specified file into a pandas DataFrame. The file may
        include various formats supported by pandas, and additional keyword
        arguments can be provided to specify how the file should be read.

        :param filename: The name or path of the file to be read.
        :type filename: str
        :param kwargs: Additional parameters to customize how the file is read.
        :return: A pandas DataFrame containing the data from the file.
        :rtype: pd.DataFrame
        """
        pass

    def can_yield(self, configuraton: FileLoaderConfiguration|None = None) -> bool:
        """
        Return true if the class can yield an interator instead of return a single data frame
        :return: True if the yield file method is available
        """
        return False

    def yield_file(self, filename: str, **kwargs) -> Iterator[pd.DataFrame]:
        """
        Yield DataFrames from a file, processing its contents as per the provided
        configuration parameters. This method is intended to allow efficient,
        incremental processing of large datasets by handling data in a streaming
        fashion.

        :param filename: The path to the file to be processed.
        :param kwargs: Additional configuration parameters to customize how the file
            should be processed.
        :return: An iterator that yields pandas DataFrames, each representing a
            portion of the processed file contents.
        """
        pass

    def reduce_file_paths(self, configuration: FileLoaderConfiguration, pancham_configuration: PanchamConfiguration | None) -> Iterator[str | dict[str, str]]:
        """
        Reduces file paths according to a given configuration. It utilizes a specified
        source directory, if provided, to prepend to each file path found within the
        configuration. The `configuration` can contain paths in string or list format.
        The method ensures that each file path is processed with the required source
        prepended, if applicable.

        :param configuration: A configuration object containing the file path(s) to
            process; can be a single file path (string) or a list of file paths.
        :type configuration: DataFrameConfiguration
        :param pancham_configuration: Optional additional configuration object that
            may include a source directory to prepend to each file path.
        :type pancham_configuration: PanchamConfiguration | None
        :return: An iterator over the processed file paths with the source directory
            prepended (if provided).
        :rtype: iter[str]
        """
        def prepend_source(file_path: str) -> str:
            if pancham_configuration is not None and pancham_configuration.source_dir is not None:
                return f"{pancham_configuration.source_dir}/{file_path}"
            return file_path

        if type(configuration.file_path) is str:
            yield prepend_source(configuration.file_path)

        if type(configuration.file_path) is list:
            for file_path in configuration.file_path:
                yield prepend_source(file_path)


class ExcelFileLoader(FileLoader):
    """
    Represents a loader for Excel files, extending the functionality of a generic
    file loader. This class provides methods to read Excel files into Pandas
    DataFrame objects based on configurations or specific file settings.

    :ivar supported_formats: Specifies the file formats that this loader supports.
    :type supported_formats: list
    :ivar default_sheet: Name of the default sheet to use if not specified.
    :type default_sheet: str
    """

    def read_file(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Reads a file and returns its data as a Pandas DataFrame. This method specifically
        targets Excel files and requires a sheet name to be specified in the additional
        keyword arguments. It raises an exception if the sheet name is not provided.

        :param filename: The path to the Excel file to be read.
        :type filename: str
        :param kwargs: Additional keyword arguments, including the 'sheet' parameter,
            which specifies the name of the sheet to read from the Excel file.
            This parameter is mandatory for proper functionality.
        :return: A Pandas DataFrame containing the data from the specified sheet.
        :rtype: pandas.DataFrame

        :raises ValueError: If the 'sheet' keyword argument is not present, indicating
            that the required sheet name was not supplied.
        """
        if "sheet" not in kwargs:
            raise ValueError("Sheet name must be provided for Excel files.")

        return pd.read_excel(filename, sheet_name=kwargs["sheet"])

    def can_yield(self, configuraton: FileLoaderConfiguration|None = None) -> bool:
        return True

    def yield_file(self, filename: str, **kwargs) -> Iterator[pd.DataFrame]:
        """
        Reads data from a file and yields it as a pandas DataFrame. Supports specifying
        additional options like the sheet name for cases where the file format is
        spreadsheet-based.

        :param filename: The name of the file to be read.
        :param kwargs: Arbitrary keyword arguments, such as 'sheet' for specifying
            the sheet name when reading spreadsheet files.
        :return: An iterator over the read pandas DataFrame.
        :rtype: Iterator[pd.DataFrame]
        """
        yield self.read_file(filename, sheet=kwargs.get("sheet", None))



class YamlFileLoader(FileLoader):

    def read_file(self, filename: str, **kwargs) -> pd.DataFrame:
        if "key" not in kwargs:
            raise ValueError("Key must be provided for Yaml files.")

        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
            if kwargs["key"] not in data:
                raise ValueError(f"{kwargs['key']} not in {filename}")

            return pd.DataFrame(data[kwargs["key"]])

class JsonFileLoader(FileLoader):

    def read_file(self, filename: str, **kwargs) -> pd.DataFrame:
        reporter = get_reporter()

        reporter.report_debug("Loading json file")
        if "key" not in kwargs or kwargs["key"] is None:
            return pd.read_json(filename)

        with open(filename, 'r') as file:
            data = json.load(file)

            keyed_data = data[kwargs["key"]]

            return pd.DataFrame(keyed_data)

    def can_yield(self, configuraton: FileLoaderConfiguration|None = None) -> bool:
        return True

    def yield_file(self, filename: str, **kwargs) -> Iterator[pd.DataFrame]:
        reporter = get_reporter()
        reporter.report_debug("Starting Json chunk load")
        for data in read_json_chunk(filename, key=kwargs.get("key", None), chunk_size=kwargs.get('chunk_size', 1000)):
            df = pd.DataFrame(data)
            reporter.report_debug(f"Loading iterator - size {len(data)}")
            reporter.report_debug(df)
            yield df


class CsvFileLoader(FileLoader):
    """
    Handles loading and reading CSV files.

    This class provides functionality to read CSV files and convert them into
    pandas DataFrame objects. It is a specialized implementation of the
    FileLoader interface specifically for CSV file formats.

    :ivar supported_extension: A string indicating the supported file extension
        for this loader (e.g., '.csv').
    :type supported_extension: str
    """

    def read_file(self, filename: str, **kwargs) -> pd.DataFrame:
        return pd.read_csv(filename)
