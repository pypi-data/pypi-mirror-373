import pandas as pd

from pancham.validation.not_null_validation import NotNullValidation
from pancham.validation_field import ValidationRule, ValidationInput


class TestNotNullValidation:

    def test_not_null_validation(self):
        data = pd.DataFrame({'a': ['a', None], 'b': ['1', '2']})

        validator = NotNullValidation()

        output = validator.validate(ValidationInput('not_null', data, ValidationRule('a', 'b', {})))

        assert len(output) == 1

    def test_not_null_name(self):
        validator = NotNullValidation()

        assert validator.get_name() == 'not_null'
