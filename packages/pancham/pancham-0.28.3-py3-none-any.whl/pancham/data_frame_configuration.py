from typing import Self, Type, Literal

import pandera as pa

from .file_loader_configuration import FileLoaderConfiguration
from .validation_field import ValidationField
from .data_frame_field import DataFrameField

class MergeConfiguration:
    """
    Represents the configuration for merging dataframes.

    This class is used to define the necessary parameters for merging two
    dataframes, including specifying the name of the required dataframe and
    the column names to use for joining on the left and right dataframes.

   """

    def __init__(self, required_dataframe: str, source_key: str|None = None, processed_key: str|None = None):
        self.required_dataframe = required_dataframe
        self.source_key = source_key
        self.processed_key = processed_key

class DataFrameConfiguration(FileLoaderConfiguration):
    """
    Represents a configuration for managing and processing data in a DataFrame.

    This class is designed to facilitate customization and validation of a DataFrame's
    structure, allowing specification of fields, their types, dynamic behavior, and
    schema validation. It manages fields, dynamic calculations, schema definition, and
    output configuration for a DataFrame. It is highly customizable to cater to varying
    data-processing requirements.

    :ivar file_path: The path to the data file.
    :type file_path: str
    :ivar file_type: The type of the data file (e.g., csv, excel).
    :type file_type: str
    :ivar sheet: Optional parameter defining the sheet name if the data resides in a multi-sheet file.
    :type sheet: str|None
    :ivar fields: A list containing field definitions as `DataFrameField` objects.
    :type fields: list[DataFrameField]
    :ivar output: A list of dictionaries containing output configuration for processing.
    :type output: list[dict]
    """

    def __init__(self,
                 file_path: str|list[str],
                 file_type: str,
                 name: str,
                 sheet: str|None = None,
                 key: str|None = None,
                 merge_configuration: MergeConfiguration|None = None,
                 depends_on: list[str]|None = None,
                 drop_duplicates: str|list[str]|None = None,
                 process: Literal['passthrough', 'parse', 'append'] = 'parse',
                 query: str|None = None,
                 ):
        self.file_path = file_path
        self.file_type = file_type
        self.name = name
        self.sheet = sheet
        self.key = key
        self.merge_configuration = merge_configuration
        self.depends_on = depends_on
        self.drop_duplicates = drop_duplicates
        self.query = query

        self.fields: list[DataFrameField] = []
        self.validation_rules: list[ValidationField] = []
        self.output: list = []
        self.pre_run_configuration: list[DataFrameConfiguration] = []
        self.post_run_configuration: list[DataFrameConfiguration] = []
        self.process = process

    def add_field(
            self,
            name: str = None,
            source_name: str|int = None,
            field_type: type = None,
            nullable: bool = True,
            data_frame_field:DataFrameField = None
            ) -> Self:
        """
        Adds a new field to the collection of fields. The method creates a
        new `DataFrameField` instance using the provided parameters and
        appends it to the list of fields. If a `data_frame_field` object is
        supplied, it will directly append the existing field object
        instead of creating a new one.

        :param name: The name of the field to be added. Defaults to None.
        :param source_name: The source name or identifier for the field.
        :param field_type: The Python type of the field, used to define
            its data type.
        :param nullable: A boolean flag indicating whether the field is
            nullable or not. Defaults to True.
        :param data_frame_field: An optional `DataFrameField` object. If
            provided, this object is appended directly to the list of fields.
        :return: Returns the current object to allow for method chaining.
        :rtype: Self
        """

        if data_frame_field is None:
            self.fields.append(DataFrameField(name, source_name, field_type, nullable))
        else:
            self.fields.append(data_frame_field)

        return self

    def add_dynamic_field(
            self,
            name: str = None,
            field_type: type = None,
            nullable: bool = True,
            func: callable = None,
            data_frame_field: DataFrameField = None
    ) -> Self:
        """
        Adds a dynamic field to the collection of fields in the current object. If
        `data_frame_field` is provided, it will directly append the provided
        `DataFrameField` to the collection. If `data_frame_field` is not provided,
        it constructs a new `DataFrameField` instance based on the given values
        for `name`, `field_type`, `nullable`, and `func`.

        :param name: Name of the field to be added. Defaults to None.
        :type name: str, optional
        :param field_type: Type of the field. Can be any valid Python type and is
            used to indicate what kind of data this field represents. Defaults to None.
        :type field_type: type, optional
        :param nullable: Indicates whether the field can have None values. When True,
            the field is considered nullable. Defaults to True.
        :type nullable: bool, optional
        :param func: A callable function associated with the field, typically used
            for computing derived values or transformations prior to adding this field.
        :type func: callable, optional
        :param data_frame_field: An instance of `DataFrameField` to be directly
            appended to the fields collection. If provided, other parameters (such as
            `name`, `field_type`, `nullable`, and `func`) are ignored. Defaults to None.
        :type data_frame_field: DataFrameField, optional
        :return: Returns the current instance of the class to allow chaining of
            method calls.
        :rtype: Self
        """

        if data_frame_field is None:
            dff = DataFrameField(name, source_name=None, field_type=field_type, nullable=nullable, func= func)
            self.fields.append(dff)
        else:
            self.fields.append(data_frame_field)

        return self

    @property
    def renames(self) -> dict[str, str]:
        """
        Provides an interface to compute and retrieve a dictionary of field names
        mapped from their source names, filtered to include only non-dynamic fields.

        :attribute renames: A property to compute and return the mapping of source
            field names to their corresponding field names based on specific
            conditions.

        :return: A dictionary where each key is the source name of a field and the
            corresponding value is the name of the field, limited to fields that are
            not dynamic.
        :rtype: dict[str, str]
        """
        output = {}

        for field in self.fields:
            if not field.is_dynamic():
                output[field.source_name] = field.name

        return output

    @property
    def dynamic_fields(self) -> list[DataFrameField]:
        """
        Filters and returns all dynamic fields within the list of fields.

        This method inspects the list of `DataFrameField` objects stored in the
        `fields` attribute of the instance and identifies those marked as dynamic.
        A dynamic field is identified based on the `is_dynamic` property of the
        `DataFrameField`.

        :returns: A list containing all `DataFrameField` objects that are dynamic.
        :rtype: list[DataFrameField]
        """

        return list(filter(lambda x: x.is_dynamic(), self.fields))

    @property
    def output_fields(self) -> list[str]:
        """
        Provides a method to output the names of all fields as a list of strings from
        the `fields` attribute of the instance. The method applies a mapping function
        to extract the `.name` property of each field present in `fields`.

        :raises AttributeError: If any object in `fields` does not have a `name` attribute
          or if `fields` is not iterable.
        :return: A list of strings containing the `name` property of each field in `fields`.
        :rtype: list[str]
        """
        output = []
        for field in self.fields:
            if not field.has_df_func():
                output.append(field.name)
        return output

    @property
    def schema(self) -> pa.DataFrameSchema:
        """
        Creates and returns a DataFrame schema object defined by the fields and their
        corresponding properties in the `fields` attribute.

        Each field in the `fields` attribute is iterated over to construct a
        dictionary of column schema where the key is the field name and the
        value is a `pa.Column` object. The `pa.DataFrameSchema` object is then
        created using this dictionary to validate DataFrame structures.

        :raises None: This function does not raise any exceptions.

        :return: A `pa.DataFrameSchema` object, constructed based on the defined
                 fields and their properties.
        :rtype: pa.DataFrameSchema
        """

        schema: dict[str, pa.Column] = {}

        for f in self.fields:
            schema[f.name] = pa.Column(f.field_type, nullable=f.nullable)

        return pa.DataFrameSchema(schema)

    @property
    def cast_values(self) -> dict[str, Type]:
        """
        Converts provided field types into a mapping of field names and their associated
        cast types based on the `cast_type` attribute of fields.

        This method iterates over all defined fields, checks if a `cast_type` is specified,
        and creates a dictionary mapping the field names to their corresponding field
        types. If a field does not have a `cast_type`, it is not included in the resulting
        dictionary.

        :return: A dictionary mapping field names (str) to their respective
            associated types (`Type`) if they have a `cast_type`. Fields without a
            `cast_type` are excluded.
        :rtype: dict[str, Type]
        """

        casts = {}
        for field in self.fields:
            if field.cast_type:
                casts[field.name] = field.field_type

        return casts

    def get_field_type(self, field_name: str):
        """
        Fetches the type of a field with the specified name.

        Iterates through the list of fields to find a field whose name matches
        the provided field name, and returns its corresponding type. If no
        matching field is found, returns None.

        :param field_name: The name of the field for which the type
            needs to be fetched.
        :return: The type of the field if found, otherwise None.
        """
        for field in self.fields:
            if field.name == field_name:
                return field.field_type
        return None

    def add_output(self, output_configuration) -> Self:
        """
        Appends the given output configuration to the output list of the current
        instance. This method is chainable, allowing for sequential method calls.

        :param output_configuration: The output configuration object to
            append. It should be of type `OutputWriter`.
        :return: The current instance of the class with the updated
            output list.
        """
        self.output.append(output_configuration)
        return self

    def __hash__(self):
        """
        Computes and returns the hash value of the `FileLoaderConfiguration` instance
        created with the current object's attributes.

        :return: The hash value of the `FileLoaderConfiguration` instance.
        :rtype: int
        """
        loader = FileLoaderConfiguration(
            sheet=self.sheet,
            file_type=self.file_type,
            key=self.key,
            file_path=self.file_path,
            use_iterator=self.use_iterator,
            chunk_size=self.chunk_size,
            query=self.query
        )

        return hash(loader)
