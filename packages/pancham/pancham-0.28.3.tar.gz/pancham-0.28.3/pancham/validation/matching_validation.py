from pancham.validation_field import ValidationStep, ValidationInput, ValidationFailure

class MatchingValidation(ValidationStep):

    def validate(self, input: ValidationInput) -> list[ValidationFailure]:
        """
        Validates the test data against the given rules and expected values. The method
        checks whether a row satisfying the provided `search_field` and `search_value`
        conditions exists in the `test_data`. If such a row exists, it further validates
        whether the `test_field` value in the row matches the `expected_value`. If any
        validation step fails, the method returns a list of `ValidationFailure` objects
        describing the issues.

        :param input: The validation input containing test data, rules, and properties
                      including the `search_field`, `search_value`, `expected_value`,
                      and `test_field`.
        :type input: ValidationInput
        :return: A list of `ValidationFailure` objects representing the validation
                 errors, if any. An empty list is returned when no validation errors
                 are found.
        :rtype: list[ValidationFailure]
        """
        search_field = input.rule.properties.get("search_field")
        search_value = input.rule.properties.get("search_value")
        expected_value = input.rule.properties.get("expected_value")
        test_field = input.rule.test_field

        # Find the row in test_data where search_field matches search_value
        matching_row = input.test_data[input.test_data[search_field] == search_value]

        validation_failures = []
        if matching_row.empty:
            failure = ValidationFailure(
                failed_id=expected_value,
                test_name=self.get_name(),
                message=f"No matching row found for {search_field} = {search_value}."
            )
            validation_failures.append(failure)
        else:
            # Validate the expected value against the test_field value
            if matching_row.iloc[0][test_field] != expected_value:
                failure = ValidationFailure(
                    failed_id=matching_row.iloc[0][input.rule.id_field],
                    test_name=self.get_name(),
                    message=f"Expected value {expected_value} does not match {test_field} value."
                )
                validation_failures.append(failure)

        return validation_failures

    def get_name(self) -> str:
        return "match"