from pancham.validation_field import ValidationStep, ValidationInput, ValidationFailure

class NotNullValidation(ValidationStep):
    """
    Implements a validation rule to check for null values in a given field of the test data.

    This class is used to identify null values in the specified test field within the
    provided test data. It generates validation failures for each null value found,
    allowing for validation of data completeness and integrity within the context
    of whatever dataset is being processed.

    :ivar data_description: Description of the data this rule is applied on.
    :type data_description: str
    :ivar validation_rule: Short explanation of the validation criteria.
    :type validation_rule: str
    """

    def validate(self, input: ValidationInput) -> list[ValidationFailure]:
        test_data = input.test_data
        test_field = input.rule.test_field
        null_values = test_data[test_data[test_field].isnull()]

        validation_failures = []
        for index, row in null_values.iterrows():
            failure = ValidationFailure(
                failed_id=row[input.rule.id_field],
                test_name=self.get_name(),
                message=f"value for {test_field} is null.")
            validation_failures.append(failure)

        return validation_failures


    def get_name(self) -> str:
        return "not_null"