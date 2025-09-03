from configuration.regex_match_field_parser import RegexMatchFieldParser

class TestRegexFieldMatcher:

    def test_can_parse(self):
        field = {
            'name': 'a',
            'func': {
                'regex_match':{}
            }
        }

        parser = RegexMatchFieldParser()

        assert parser.can_parse_field(field)

    def test_parse_field(self):
        field = {
            'name': 'a',
            'func': {
                'regex_match': {
                    'source_name': 'b',
                    'pattern': 'abc'
                }
            }
        }


        parser = RegexMatchFieldParser()

        data_field = parser.parse_field(field)

        assert data_field.func({'b': 'abc'}) == True
        assert data_field.func({'b': 'xbc'}) == False

    def test_parse_field_pattern(self):
        field = {
            'name': 'a',
            'func': {
                'regex_match': {
                    'source_name': 'b',
                    'pattern': '\w+@\w+\.\w+'
                }
            }
        }


        parser = RegexMatchFieldParser()

        data_field = parser.parse_field(field)

        assert data_field.func({'b': 'bob@example.com'}) == True
        assert data_field.func({'b': 'xbc'}) == False