import pytest

from configuration.to_int_field_parser import ToIntFieldParser

class TestToIntFieldParser:

    def test_can_parse(self):
        parser = ToIntFieldParser()
        field = {
            'name': 'a',
            'func': {
                'to_int': {}
            }
        }

        assert parser.can_parse_field(field) == True

    def test_parse(self):
        parser = ToIntFieldParser()
        field = {
            'name': 'a',
            'func': {
                'to_int': {
                    'source_name': 'b'
                }
            }
        }

        data_field = parser.parse_field(field)

        assert data_field.name == 'a'

        input  = {'b': '4'}
        assert data_field.func(input) == 4

    def test_parse_error_and_default(self):
        parser = ToIntFieldParser()
        field = {
            'name': 'a',
            'func': {
                'to_int': {
                    'source_name': 'b',
                    'error_value': 0,
                }
            }
        }

        data_field = parser.parse_field(field)

        assert data_field.name == 'a'

        input  = {'b': 'abc'}
        assert data_field.func(input) == 0

    def test_parse_error_and_no_default(self):
        parser = ToIntFieldParser()
        field = {
            'name': 'a',
            'func': {
                'to_int': {
                    'source_name': 'b',
                }
            }
        }

        data_field = parser.parse_field(field)

        assert data_field.name == 'a'

        input = {'b': 'abc'}

        with pytest.raises(ValueError):
            data_field.func(input)


    def test_parse_error_and_no_source(self):
        parser = ToIntFieldParser()
        field = {
            'name': 'a',
            'func': {
                'to_int': {
                }
            }
        }

        with pytest.raises(ValueError):
            parser.parse_field(field)