from pancham.validation_field import ValidationStep, ValidationInput, ValidationFailure

class ContainsValidation(ValidationStep):

    def validate(self, input: ValidationInput) -> list[ValidationFailure]:
        """
        Validates the input data according to the defined rules and checks if the expected values
        exist in the specified test field of the test data. If any expected value is missing,
        it logs a validation failure.

        :param input: ValidationInput object containing the validation rule and test data.
        :type input: ValidationInput
        :return: A list of ValidationFailure objects indicating the details of validation failures.
        :rtype: list[ValidationFailure]
        """
        expected_values = input.rule.properties.get("expected_values", [])
        test_field = input.rule.test_field

        validation_failures = []
        for value in expected_values:
            if value not in input.test_data[test_field].values:
                failure = ValidationFailure(
                    failed_id=None,
                    test_name=self.get_name(),
                    message=f"Expected value '{value}' not found in field '{test_field}'."
                )
                validation_failures.append(failure)

        return validation_failures

    def get_name(self) -> str:
        return "contains"