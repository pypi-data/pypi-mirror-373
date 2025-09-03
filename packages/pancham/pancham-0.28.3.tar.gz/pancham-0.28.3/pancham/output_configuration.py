from dataclasses import dataclass

import pandas as pd

from pancham.data_frame_configuration import DataFrameConfiguration
from pancham.data_frame_loader import DataFrameLoader

class OutputWriter:
    """
    Write the output data to the target system
    """

    def __init__(self, root_configuration: dict):
        self.root_configuration = root_configuration

    def write(self, data: pd.DataFrame,
              success_handler: DataFrameConfiguration|None = None,
              failure_handler: DataFrameConfiguration|None = None,
              loader: DataFrameLoader|None = None
              ):
        """
        Writes the output data to the target system
        :param data:
        :param success_handler:
        :param failure_handler:
        :param loader:
        :return: None
        """
        pass


@dataclass
class OutputActivitySet:
    """
    Output objects that will be loaded as part of the configuration
    """

    primary_writer: OutputWriter
    success_handler: DataFrameConfiguration|None
    failure_handler: DataFrameConfiguration|None


class OutputConfiguration:
    """
    Represents the configuration used for output operations.

    This class encapsulates settings and functionality specific to managing
    the configuration of data output processes. It is used to determine if
    certain configurations can be applied and to apply them to a given dataset.

    :ivar attribute1: Description of attribute1.
    :type attribute1: type
    :ivar attribute2: Description of attribute2.
    :type attribute2: type
    """

    def can_apply(self, configuration: dict):
        """
        Determines whether the given configuration is eligible for
        application based on the specified logic. This method evaluates
        the contents of the input dictionary and returns a boolean value
        indicating whether the configuration meets the required conditions.

        :param configuration: A dictionary containing configuration values
            to be checked for applicability.
        :type configuration: dict
        :return: A boolean indicating if the configuration can be applied.
        :rtype: bool
        """
        pass

    def to_output_writer(self, configuration: dict) -> OutputWriter:
        """
        Converts the given input configuration dictionary into an output writer.

        :param configuration: Input configuration dictionary containing the necessary
            data to be transformed.
        :type configuration: dict
        :return: The transformed output configuration dictionary based on the input
            configuration.
        :rtype: OutputWriter
        """
        pass

    def extract_configuration_by_key(self, configuration: dict, key: str) -> dict|None:
        """
        Extracts a specific configuration from a dictionary based on a given key.

        This function searches within the 'output' section of the provided
        configuration dictionary to find a matching entry where the 'output_type'
        matches the specified key. If a match is found, the corresponding dictionary
        is returned. If the 'output' section is not present in the configuration or no
        match is found, the function returns None.

        :param configuration: A dictionary containing the data to be searched, which
            should include an 'output' key with a list of configurations.
        :param key: The key used to match the 'output_type' in the entries within the
            'output' list.
        :return: A dictionary representing the matched configuration, or None if no
            match is found.
        """
        if 'output_type' in configuration and configuration['output_type'] == key:
            return configuration

        if not 'output' in configuration:
            return None

        matched: dict|None = None

        for out in configuration['output']:
            if out['output_type'] == key:
                matched = out
                break

        return matched

