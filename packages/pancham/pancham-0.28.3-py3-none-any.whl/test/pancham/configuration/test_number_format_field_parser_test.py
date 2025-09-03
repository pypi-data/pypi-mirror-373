import pytest

from configuration.number_format_field_parser import NumberFormatFieldParser

class TestNumberFormatFieldParser:

    def test_can_parse(self):
        field = {
            'name': 'a',
            'func': {
                'number_format': {}
            }
        }

        parser = NumberFormatFieldParser()
        assert parser.can_parse_field(field)

    def test_parse_padded_number(self):
        field = {
            'name': 'Padded',
            'source_name': 'a',
            'func': {
                'number_format': {
                    'format': '{:0>4}'
                }
            }
        }

        input = {
            'a': 34
        }

        parser = NumberFormatFieldParser()

        data_field = parser.parse_field(field)
        assert data_field.func(input) == '0034'


    def test_parse_padded_number_with_decimal(self):
        field = {
            'name': 'Padded',
            'source_name': 'a',
            'func': {
                'number_format': {
                    'format': '{:0>7.2f}'
                }
            }
        }

        input = {
            'a': 34.1234
        }

        parser = NumberFormatFieldParser()

        data_field = parser.parse_field(field)
        assert data_field.func(input) == '0034.12'
