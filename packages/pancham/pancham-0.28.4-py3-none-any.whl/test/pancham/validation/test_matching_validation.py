from pancham.validation import MatchingValidation

class TestMatchingValidation:

    def test_name(self):
        validation = MatchingValidation()

        assert validation.get_name() == "match"