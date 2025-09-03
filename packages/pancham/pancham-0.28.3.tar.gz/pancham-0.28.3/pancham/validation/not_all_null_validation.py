from pancham.validation_field import ValidationStep, ValidationInput, ValidationFailure

class NotAllNullValidation(ValidationStep):

    def validate(self, input: ValidationInput) -> list[ValidationFailure]:
        """
        Validates the input data to ensure that specified test fields in the
        data are not entirely null. It iterates through the test fields and checks
        if any column contains only null values. If such a column is found, a
        validation failure is recorded.

        :param input: An instance of ``ValidationInput`` containing the test_data
            to validate and rule properties specifying the test fields to check.
        :type input: ValidationInput
        :return: A list of ``ValidationFailure`` objects indicating which columns
            (if any) failed the validation by containing only null values.
        :rtype: list[ValidationFailure]
        """
        test_data = input.test_data
        validation_failures = []
        columns = input.rule.properties["test_fields"]

        for column in columns:
            if test_data[column].notnull().sum() == 0:  # Check if all values in the column are null
                failure = ValidationFailure(
                    failed_id=None,  # No specific ID associated with this failure
                    test_name=self.get_name(),
                    message=f"No non-null values found in column: {column}"
                )
                validation_failures.append(failure)

        return validation_failures

    def get_name(self) -> str:
        return "not_all_null"


