import pytest

from pancham.configuration.database_multi_field_search_parser import DatabaseMultiFieldSearchParser


class TestMultiFieldSearchParser:

    def test_can_parse(self):
        field = {
            'name': 'a',
            'func': {
                'database_multi_field_search': {}
            }
        }

        parser = DatabaseMultiFieldSearchParser()

        assert parser.can_parse_field(field)

    def test_missing_values(self):
        field = {
            'func': {
                'database_multi_field_search': {}
            }
        }

        parser = DatabaseMultiFieldSearchParser()

        with pytest.raises(ValueError):
            parser.parse_field(field)

    def test_valid_values(self):
        field = {
            'name': 'a',
            'field_type': str,
            'func': {
                'database_multi_field_search': {
                    'table_name': 'a',
                    'value_column': 'b',
                    'search': [
                    ]
                }
            }
        }

        parser = DatabaseMultiFieldSearchParser()

        out = parser.parse_field(field)

        assert out.name == 'a'
