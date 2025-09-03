import pandas as pd

from pancham.validation.one_of_validation import OneOfValidation
from pancham.validation_field import ValidationInput, ValidationRule


class TestOneOfValidation:

    def test_name(self):
        validator = OneOfValidation()

        assert validator.get_name() == "one_of"

    def test_validate(self):
        df = pd.DataFrame({'a': ['Customer', 'User', 'Other'], 'b': [1, 2, 3]})

        rule = ValidationRule('a', 'b', {'allowed_values': ['Customer', 'User']})
        input = ValidationInput('one_of', df, rule)

        output = OneOfValidation().validate(input)

        assert len(output) == 1