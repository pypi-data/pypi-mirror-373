import pytest

from configuration.static_field_parser import StaticFieldParser


class TestStaticFieldParser:

    def test_can_parse(self):
        field = {
            'name': 'a',
            'func': {
                'static': {}
            }
        }

        parser = StaticFieldParser()
        assert parser.can_parse_field(field)

    def test_extract_value(self):
        field = {
            'name': 'a',
            'field_type': bool,
            'func': {
                'static': {
                    'value': True
                }
            }
        }

        parser = StaticFieldParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'a'
        assert data_field.func(None) == True

    def test_extract_missing_value(self):
        field = {
            'name': 'a',
            'field_type': bool,
            'func': {
                'static': {
                }
            }
        }

        parser = StaticFieldParser()

        with pytest.raises(ValueError):
            parser.parse_field(field)