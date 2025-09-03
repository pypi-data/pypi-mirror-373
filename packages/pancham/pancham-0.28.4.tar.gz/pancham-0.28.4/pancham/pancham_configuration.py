import yaml
import os
from benedict import benedict

class PanchamConfiguration:
    """
    Represents the configuration settings for the Pancham application.

    This class provides access to various configurations needed by the Pancham
    application. It includes functionality for retrieving the database connection
    string and other configuration parameters essential for application operation.

    :ivar config_data: Contains the raw configuration data as loaded from a
        configuration file or environment settings.
    :type config_data: dict
    :ivar environment: Represents the current environment in which the application
        is running (e.g., 'development', 'production').
    :type environment: str
    """

    @property
    def database_connection(self) -> str:
        """
        Provides the database connection string for the application. This property
        retrieves the configured connection string used to interface with the
        database layer, supporting operations that deal with persistent data storage.

        :return: The connection string to establish a database connection.
        :rtype: str
        """
        return ""

    @property
    def source_dir(self) -> str:
        """
        Provides access to the source directory as a string. This property allows you
        to retrieve the path of the directory from where the source files are managed.

        :raises AttributeError: If the value is accessed before being properly initialized.
        :return: A string representing the path of the source directory.
        :rtype: str
        """
        return ""

    @property
    def debug_status(self) -> bool:
        """
        This property retrieves the current debug status of the instance. The value returned
        indicates if debugging is active or not. The returned value is boolean and immutable.

        :rtype: bool
        :return: The debug status of the instance. Returns `False` if debugging mode is not
          enabled.
        """
        return False


    @property
    def disable_schema_validation(self) -> bool:
        """
        Represents a property that determines whether schema validation should
        be disabled.

        This property is useful for enabling or disabling schema validation in
        certain operations where schema correctness needs to be either enforced
        or bypassed.

        :return: Boolean value indicating whether schema validation is
            disabled. Returns True if schema validation is disabled,
            otherwise False.
        :rtype: bool
        """
        return False

    @property
    def reporter_name(self) -> str:
        """
        Provides access to the reporter's name.

        This property retrieves the name of the reporter associated with an instance.
        The reporter name is a read-only attribute and can be used to identify
        or log relevant information related to the reporter.

        :return: The name of the reporter.
        :rtype: str
        """
        return ""

    @property
    def mapping_files(self) -> list[str]:
        """
        Provides access to the list of mapping files. This property returns a list of strings
        that represent the file paths or identifiers for the mapped files.

        :return: The list of filenames or paths for the mapping files.
        :rtype: list[str]
        """

        return []

    @property
    def test_files(self) -> list[str]:
        """
        This property retrieves the list of test files. It returns an empty list
        if no test files are defined.

        :return: A list containing the names of test files.
        :rtype: list[str]
        """
        return []

    @property
    def enabled_features(self) -> list[str]:
        """
        Retrieves the list of enabled features.

        This property provides a list of feature names that are currently
        enabled in the system.

        Returns:
            list[str]: A list of strings representing the names of enabled
            features.
        """
        return []

    def has_feature_enabled(self, feature: str) -> bool:
        """
        Checks if a specified feature is enabled for the current instance.

        This method verifies whether the provided feature exists within the list
        of features marked as enabled.

        Parameters:
        feature: str
            The name of the feature whose enabled status is being checked.

        Returns:
        bool
            True if the feature is enabled, False otherwise.
        """
        return feature in self.enabled_features

class OrderedPanchamConfiguration(PanchamConfiguration):

    def __init__(self, config_file_path: str|None):
        self.config_file_path = config_file_path
        self.config_data = {}
        self.config_file = {}

    @property
    def database_connection(self) -> str:
        return self.__get_config_item("database_connection", "PANCHAM_DATABASE_CONNECTION", "database.connection")

    @property
    def debug_status(self) -> bool:
        return self.__get_config_item("debug_status", "PANCHAM_DEBUG_STATUS", "debug.status")

    @property
    def source_dir(self) -> str:
        return self.__get_config_item("source_dir", "PANCHAM_SOURCE_DIR", "source.dir")

    @property
    def disable_schema_validation(self) -> bool:
        return self.__get_config_item("disable_schema_validation", "PANCHAM_DEBUG_DISABLE_SCHEMA_VALIDATION", "debug.disable_schema_validation")

    @property
    def reporter_name(self) -> str:
        return self.__get_config_item("reporter_name", "PANCHAM_DEBUG_REPORTER", "debug.reporter")

    @property
    def enabled_features(self) -> list[str]:
        features = self.__get_config_item("enabled_features", "PANCHAM_ENABLED_FEATURES", "enabled_features")

        if isinstance(features, str):
            return features.split(",")

        return super().enabled_features

    @property
    def mapping_files(self) -> list[str]:
        """
        Get the list of mapping files

        If mapping files are used, they must be in the configuration file and not in the
        :return:
        """
        data = self.__get_config_file_data()
        return data.get("mapping_files", [])

    @property
    def test_files(self):
        """
        Retrieves and returns the list of test files defined in the configuration file.

        This method accesses a configuration file through a helper method, processes
        its contents, and extracts a list of test files from a specific key.

        :return: The list of test files, empty if no such key exists.
        :rtype: List[Any]
        """
        data = self.__get_config_file_data()
        return data.get("test_files", [])

    def __get_config_item(self, name: str, env_var: str|None = None, config_name: str|None = None) -> str|bool|None:
        """
        Retrieve the configuration item based on ordering priority from configuration data,
        environment variables, or configuration file data. This method checks and returns
        the value for the requested configuration item by following the hierarchy:
        config_data > environment variable > configuration file.

        :param name: The key to retrieve the configuration item from config_data.
        :type name: str
        :param env_var: The environment variable name, used as an alternative lookup.
                        This is optional and allows None.
        :type env_var: str | None
        :param config_name: The corresponding key in the configuration file if the value
                            is not found in config_data or environment variables. This is
                            optional and allows None.
        :type config_name: str | None
        :return: The resolved configuration value associated with the provided name.
        :rtype: str
        """
        if name in self.config_data:
            return self.config_data[name]

        if env_var is not None and env_var in os.environ:
            value = os.environ[env_var]
            self.config_data[name] = value
            return value

        config_file = self.__get_config_file_data()
        benedict_config_file = benedict(config_file)
        if config_name is not None and config_name in benedict_config_file:
            value = benedict_config_file[config_name]
            self.config_data[name] = value
            return value

    def __get_config_file_data(self) -> dict:
        """
        Retrieves data from a configuration file. If the `config_file` attribute is
        non-empty, it directly returns its content. Otherwise, it reads the configuration
        file from the path specified by the `config_file_path` attribute, parses it,
        and stores the results in the `config_file` attribute before returning it. If
        `config_file_path` is `None`, it returns an empty dictionary.

        :return: Parsed configuration data from the file or an empty dictionary.
        :rtype: dict
        """
        if self.config_file_path is None:
            return {}

        if len(self.config_file) > 0:
            return self.config_file

        with open(self.config_file_path, "r") as config_file:
            self.config_file = yaml.safe_load(config_file)
            return self.config_file

class StaticPanchamConfiguration(PanchamConfiguration):
    """
    Configuration class for static Pancham projects.

    This class extends the PanchamConfiguration class to provide static
    configuration properties and parameters used in static project-oriented
    settings. It allows users to specify database connection details,
    source directories, debugging options, and schema validation
    preferences. It is specifically useful for use cases requiring predefined
    and constant configuration settings.

    :ivar database_connection: Connection string used to interact with the
        database.
    :type database_connection: str
    :ivar debug_status: Debugging mode status indicating whether debugging
        is enabled.
    :type debug_status: bool
    :ivar source_dir: Directory path to the source code or project files.
    :type source_dir: str
    :ivar disable_schema_validation: Boolean flag to determine whether
        schema validation needs to be disabled.
    :type disable_schema_validation: bool
    """

    def __init__(self,
                 database_connection: str,
                 debug_status: bool,
                 source_dir: str,
                 disable_schema_validation: bool):
        self.__database_connection = database_connection
        self.__debug_status = debug_status
        self.__source_dir = source_dir
        self.__disable_schema_validation = disable_schema_validation

    @property
    def database_connection(self) -> str:
        return self.__database_connection

    @property
    def source_dir(self) -> str:
        return self.__source_dir

    @property
    def debug_status(self) -> bool:
        return self.__debug_status

    @property
    def disable_schema_validation(self) -> bool:
        return self.__disable_schema_validation

