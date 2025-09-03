from pancham.configuration.concat_field_parser import ConcatFieldParser


class TestConcatFieldParser:

    def test_parse(self):
        paser = ConcatFieldParser()
        field = {
            'name': 'a',
            'func': {
                'concat': {}
            }
        }

        assert paser.can_parse_field(field)

    def test_run_concat(self):
        paser = ConcatFieldParser()
        field = {
            'name': 'a',
            'func': {
                'concat': {
                    'fields': ['a', 'b']
                }
            }
        }

        data = {
            'a': 'Hello',
            'b': 'World'
        }

        out = paser.parse_field(field)

        assert out.name == 'a'
        assert out.func(data) == 'Hello World'


    def test_run_concat_with_join(self):
        paser = ConcatFieldParser()
        field = {
            'name': 'a',
            'func': {
                'concat': {
                    'fields': ['a', 'b'],
                    'join': ', '
                }
            }
        }

        data = {
            'a': 'Hello',
            'b': 'World'
        }

        out = paser.parse_field(field)

        assert out.name == 'a'
        assert out.func(data) == 'Hello, World'


    def test_run_concat_with_empty_values(self):
        paser = ConcatFieldParser()
        field = {
            'name': 'a',
            'func': {
                'concat': {
                    'fields': ['a', 'b', 'c']
                }
            }
        }

        data = {
            'a': 'Hello',
            'b': 'World',
            'c': '    '
        }

        out = paser.parse_field(field)

        assert out.name == 'a'
        assert out.func(data) == 'Hello World     '


    def test_run_concat_with_empty_values_and_trim_ends(self):
        paser = ConcatFieldParser()
        field = {
            'name': 'a',
            'func': {
                'concat': {
                    'fields': ['a', 'b', 'c'],
                    'trim_ends': True
                }
            }
        }

        data = {
            'a': 'Hello',
            'b': 'World',
            'c': '    '
        }

        out = paser.parse_field(field)

        assert out.name == 'a'
        assert out.func(data) == 'Hello World'


    def test_run_concat_with_empty_values_and_trim_all(self):
        paser = ConcatFieldParser()
        field = {
            'name': 'a',
            'func': {
                'concat': {
                    'fields': ['a', 'b', 'c'],
                    'trim_all': True
                }
            }
        }

        data = {
            'a': 'Hello',
            'b': '   World',
            'c': '    '
        }

        out = paser.parse_field(field)

        assert out.name == 'a'
        assert out.func(data) == 'Hello World'


    def test_run_concat_with_empty_values_and_trim_all_and_number(self):
        paser = ConcatFieldParser()
        field = {
            'name': 'a',
            'func': {
                'concat': {
                    'fields': ['a', 'b', 'c'],
                    'trim_all': True
                }
            }
        }

        data = {
            'a': 'Hello',
            'b': 123.45,
            'c': '    '
        }

        out = paser.parse_field(field)

        assert out.name == 'a'
        assert out.func(data) == 'Hello'