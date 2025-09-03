from typing import Type, Callable
import pandas as pd

class DataFrameField:
    """
    Provides configuration for a field or change within the dataframe.

    There are 3 types of field that will be available:
        1. Renamed field - These are fields that are in the source data and just get renamed
        2. Func fields - These are fields that use a function in the dataframe apply method to create a new field
        3. Dataframe func fields - These return a new data frame and can make changes like exploding or deduplicating the
        entire dataframe.

    :ivar name: Name of the field, typically used to reference it programmatically.
    :type name: str
    :ivar source_name: Original name of the field in the source file,
        which can be a string or an integer index.
    :type source_name: str | int
    :ivar field_type: The expected type of data in this field.
    :type field_type: Type
    :ivar nullable: Indicator of whether this field can contain null or missing values.
    :type nullable: bool
    :ivar func: A callable function that processes a DataFrame and extracts a value
        for this field. It can return various types including int, str, None,
        bool, or a pandas Series. None if no processing function is defined.
    :type func: Callable[[pd.DataFrame], int | str | None | bool | pd.Series] | None
    :ivar suppress_errors: Flag to indicate whether errors should be suppressed for a
        dynamic field.
    :type suppress_errors: bool
    :ivar cast_type: Flag to indicate if the type should be changed to the field type
    :type: cast_type: bool
    """

    def __init__(
            self,
            name: str,
            source_name: str|int|None,
            field_type: Type,
            nullable: bool = True,
            func: Callable[[dict], int|str|None|bool|pd.Series]|None = None,
            suppress_errors: bool = False,
            cast_type: bool = False,
            df_func: Callable[[pd.DataFrame], pd.DataFrame] | None = None,
    ) -> None:
        self.name = name
        self.source_name = source_name
        self.field_type = field_type
        self.nullable = nullable
        self.func = func
        self.suppress_errors = suppress_errors
        self.cast_type = cast_type
        self.df_func = df_func

    def is_dynamic(self) -> bool:
        return self.func is not None or self.df_func is not None

    def has_df_func(self) -> bool:
        """
        Checks if the object has a defined dataframe function.

        This method evaluates whether the attribute `df_func` within the object is
        not set to `None`. It serves as an identifier to determine if the object
        has a valid dataframe function assigned. Useful for ensuring that the
        required dataframe functionality exists prior to performing operations
        relying on it.

        :return: Indicates whether the dataframe function is defined.
        :rtype: bool
        """
        return self.df_func is not None

    def __str__(self) -> str:
        return f"Name: {self.name}, Source Name: {self.source_name}, Type: {self.field_type}, Nullable: {self.nullable}"