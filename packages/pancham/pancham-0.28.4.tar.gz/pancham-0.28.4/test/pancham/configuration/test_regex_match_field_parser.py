from configuration.regex_extract_field_parser import RegexExtractFieldParser

class TestRegexFieldMatcher:

    def test_can_parse(self):
        field = {
            'name': 'a',
            'func': {
                'regex_extract':{}
            }
        }

        parser = RegexExtractFieldParser()

        assert parser.can_parse_field(field)

    def test_parse_field(self):
        field = {
            'name': 'a',
            'func': {
                'regex_extract': {
                    'source_name': 'b',
                    'pattern': '(B[0-9]+)'
                }
            }
        }

        parser = RegexExtractFieldParser()

        data_field = parser.parse_field(field)

        assert data_field.func({'b': 'A123-B456-C789'}) == 'B456'

    def test_parse_field_with_missing_values(self):
        field = {
            'name': 'a',
            'func': {
                'regex_extract': {
                    'source_name': 'b',
                    'pattern': '(X[0-9]+)'
                }
            }
        }

        parser = RegexExtractFieldParser()

        data_field = parser.parse_field(field)

        assert data_field.func({'b': 'A123-B456-C789'}) is None
