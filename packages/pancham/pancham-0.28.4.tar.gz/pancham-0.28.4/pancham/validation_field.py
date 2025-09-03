from dataclasses import dataclass

import pandas as pd


@dataclass
class ValidationFailure:
    """
    Represents a validation failure during a testing or verification process.

    This class is used to encapsulate details about a validation failure, including
    the identifier of the failed entity, the name of the test that was performed,
    and a message describing the reason for the failure.

    :ivar failed_id: Unique identifier of the entity that failed validation.
    :type failed_id: str | int
    :ivar test_name: Name of the test in which the failure occurred.
    :type test_name: str
    :ivar message: Detailed message describing the failure.
    :type message: str
    """

    failed_id: str | int
    test_name: str
    message: str


@dataclass()
class ValidationRule:
    test_field: str | int
    id_field: str | int
    properties: dict[str, str | int | bool | list[str] | None] | None = None


@dataclass
class ValidationInput:
    """
    Represents a data structure used for validation processes.

    This class manages the key fields and datasets required for conducting
    validation checks. It stores the relevant input data, including test data
    and optional source data, along with identifiers and key attributes for
    the validation process.

    :ivar name: Name representing the validation input.
    :type name: str
    :ivar test_field: A field used for testing, can be a string or integer.
    :type test_field: str or int
    :ivar test_data: The DataFrame containing data to be tested.
    :type test_data: pd.DataFrame
    """
    name: str
    test_data: pd.DataFrame
    rule: ValidationRule

class ValidationStep:

    def validate(self, input: ValidationInput) -> list[ValidationFailure]:
        """
        Validates the given input against predefined rules and returns a list of validation
        failures. This function is expected to perform various checks and criteria matching
        on the input and collect all failures that occur during the validation process.

        :param configuration:
        :param input: The ValidationInput object containing the data and parameters to be
            validated. It encapsulates all necessary information for the validation process.
        :type input: ValidationInput

        :return: A list of ValidationFailure objects representing all the validation issues
            found during the process. Each failure highlights a specific issue identified.
        :rtype: list[ValidationFailure]
        """
        pass

    def get_name(self) -> str:
        """
        Retrieves the name associated with the instance.

        This method is responsible for returning the name value stored or
        associated with the current object. The returned string represents
        that name.

        :return: The name of the object as a string.
        :rtype: str
        """
        pass


@dataclass()
class ValidationField:

    name: str
    rule: ValidationRule
