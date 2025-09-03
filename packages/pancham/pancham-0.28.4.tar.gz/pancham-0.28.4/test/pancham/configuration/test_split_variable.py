from pancham.configuration.split_field_parser import SplitFieldParser

class TestSplitVariable:

    def test_can_parse(self):
        split_field_parser = SplitFieldParser()
        field = {
            'name': 'a',
            'func': {
                'split': {}
            }
        }

        assert split_field_parser.can_parse_field(field)

    def test_valid_event(self):
        config = {
            'name': 'a',
            'func': {
                'split': {
                    'source_name': 'input',
                    'split_char': ';'
                }
            }
        }

        data = {
            'input': 'a'
        }

        split_field_parser = SplitFieldParser()
        output = split_field_parser.parse_field(config).func(data)

        assert output[0] == 'a'

    def test_valid_event_with_split(self):
        config = {
            'name': 'a',
            'func': {
                'split': {
                    'source_name': 'input',
                    'split_char': ';'
                }
            }
        }

        data = {
            'input': 'a;b'
        }

        split_field_parser = SplitFieldParser()
        output = split_field_parser.parse_field(config).func(data)

        assert output[0] == 'a'
        assert output[1] == 'b'

    def test_valid_event_with_multi_split(self):
        config = {
            'name': 'a',
            'func': {
                'split': {
                    'source_name': 'input',
                    'split_char': [';', ',']
                }
            }
        }

        data = {
            'input': 'a;b,c'
        }

        split_field_parser = SplitFieldParser()
        output = split_field_parser.parse_field(config).func(data)

        assert output[0] == 'a'
        assert output[1] == 'b'
        assert output[2] == 'c'

    def test_valid_event_with_remove(self):
        config = {
            'name': 'a',
            'func': {
                'split': {
                    'source_name': 'input',
                    'split_char': ';',
                    'remove_pattern': '\d+'
                }
            }
        }

        data = {
            'input': 'a2;b'
        }

        split_field_parser = SplitFieldParser()
        output = split_field_parser.parse_field(config).func(data)

        assert output[0] == 'a'
        assert output[1] == 'b'

    def test_valid_event_with_remove_post_split(self):
        config = {
            'name': 'a',
            'func': {
                'split': {
                    'source_name': 'input',
                    'split_char': ';',
                    'remove_pattern': '\d+'
                }
            }
        }

        data = {
            'input': 'a;3;b'
        }

        split_field_parser = SplitFieldParser()
        output = split_field_parser.parse_field(config).func(data)

        assert output[0] == 'a'
        assert output[1] == 'b'

    def test_valid_event_with_number_and_remove_post_split(self):
        config = {
            'name': 'a',
            'func': {
                'split': {
                    'source_name': 'input',
                    'split_char': ';',
                    'remove_pattern': '[,#a-zA-Z\s]+'
                }
            }
        }

        data = {
            'input': 'abc,Def;#1234'
        }

        split_field_parser = SplitFieldParser()
        output = split_field_parser.parse_field(config).func(data)

        assert output[0] == '1234'