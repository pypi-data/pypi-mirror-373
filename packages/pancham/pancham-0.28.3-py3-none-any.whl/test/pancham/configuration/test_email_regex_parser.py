from configuration.email_regex_match_parser import EmailRegexMatchParser


class TestEmailRegexParser:


    def test_can_parse(self):
        field = {
            'name': 'a',
            'func': {
                'email_match' : {}
            }
        }

        parser = EmailRegexMatchParser()

        assert parser.can_parse_field(field)

    def test_parse_field_pattern(self):
        field = {
            'name': 'a',
            'func': {
                'email_match': {
                    'source_name': 'b',
                }
            }
        }


        parser = EmailRegexMatchParser()

        data_field = parser.parse_field(field)

        assert data_field.func({'b': 'bob@example.com'}) == True
        assert data_field.func({'b': 'xbc'}) == False