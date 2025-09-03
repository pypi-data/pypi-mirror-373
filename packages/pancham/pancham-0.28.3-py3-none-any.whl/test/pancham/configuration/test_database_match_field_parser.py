import pytest

from configuration.database_match_field_parser import DatabaseMatchFieldParser

class MockDatabaseSearch:


    def get_mapped_id(self, search_value: str|int) -> str|int|None:

        return 10

class TestDatabaseMatchFieldParser:

    def test_can_parse_field(self):
        parser = DatabaseMatchFieldParser()
        field = {
            'name': 'a',
            'func': {
                'database_match': {}
            }
        }

        assert parser.can_parse_field(field)

    def test_parse_field(self, mocker):
        search = MockDatabaseSearch()
        mocker.patch('configuration.database_match_field_parser.get_database_search', return_value=search)

        field = {
            'name': 'a',
            'field_type': int,
            'func': {
                'database_match': {
                    'source_name': 'b',
                    'search_column': 'c',
                    'table_name': 'd',
                    'value_column': 'e'
                }
            }
        }

        parser = DatabaseMatchFieldParser()
        data_field = parser.parse_field(field)

        assert data_field.name == 'a'
        assert data_field.func({'b': 'x'}) == 10

    def test_parse_value_errors(self):
        field = {
            'name': 'a',
            'field_type': int,
            'func': {
                'database_match': {
                }
            }
        }

        parser = DatabaseMatchFieldParser()

        with pytest.raises(ValueError):
            parser.parse_field(field)


