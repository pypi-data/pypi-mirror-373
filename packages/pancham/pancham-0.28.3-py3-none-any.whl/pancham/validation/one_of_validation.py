from pancham.validation_field import ValidationStep, ValidationInput, ValidationFailure

class OneOfValidation(ValidationStep):
    """
    Ensures a field value belongs to a set of allowed values.

    This class validates that the specified field in the input data contains
    values only from a predefined set of allowed values. If any value falls
    outside this set, a validation failure is recorded for that row. This
    validation step is particularly useful for enforcing categorical or
    enumerated constraints in the data.

    :ivar description: Short description of the validation step.
    :type description: str
    """

    def validate(self, input: ValidationInput) -> list[ValidationFailure]:
        test_data = input.test_data
        test_field = input.rule.test_field
        allowed_values = input.rule.properties["allowed_values"]
        validation_failures = []

        for _, row in test_data.iterrows():
            if row[test_field] not in allowed_values:
                failure = ValidationFailure(
                    failed_id=row[input.rule.id_field],
                    test_name=self.get_name(),
                    message=f"value for {test_field} is not in allowed values.")
                validation_failures.append(failure)

        return validation_failures

    def get_name(self) -> str:
        return "one_of"