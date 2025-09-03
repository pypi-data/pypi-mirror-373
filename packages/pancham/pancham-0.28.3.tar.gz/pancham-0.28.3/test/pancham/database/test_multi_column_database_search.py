import pytest
from sqlalchemy import MetaData, Table, Column, String
import pandas as pd

from pancham.database.multi_column_database_search import MultiColumnDatabaseSearch
from pancham.database.database_engine import get_db_engine, initialize_db_engine
from pancham.reporter import PrintReporter
from pancham_configuration import PanchamConfiguration

class MockConfig(PanchamConfiguration):

    @property
    def database_connection(self) -> str:
        return "sqlite:///:memory:"

class TestMultiColumnDatabaseSearch:

    def test_search_nothing_found(self):
        initialize_db_engine(MockConfig(), PrintReporter())

        meta = MetaData()
        Table('mc_search', meta, Column("email", String), Column("order_id", String), Column("dept", String))
        meta.create_all(get_db_engine().engine)

        data  = pd.DataFrame({
            'email': ['a@example.com', 'b@example.com', 'a@example.com'],
            'order_id': ['1', '2', '3'],
            'dept': ['A', 'B', 'B']
        })

        get_db_engine().write_df(data, 'mc_search')

        search = MultiColumnDatabaseSearch('mc_search', 'order_id')

        value = search.get_mapped_id({'email': 'c@example.com'})
        assert value is None

        first_value = search.get_mapped_id({'email': 'a@example.com'})
        assert first_value == '1'

        second_value = search.get_mapped_id({'email': 'a@example.com', 'dept': 'B'})
        assert second_value == '3'

    def test_search_empty_options(self):
        search = MultiColumnDatabaseSearch('mc_search', 'order_id')

        value = search.get_mapped_id({})
        assert value is None

    def test_build_static_search(self):
        data = dict()
        search_options = [
            {"type": "static", "value": "abc", "search_column": "dept"}
        ]

        search = MultiColumnDatabaseSearch('mc_search', 'order_id')
        search_values = search.build_search_values(data, search_options)

        assert search_values == {'dept': 'abc'}

    def test_build_invalid_search(self):
        data = dict()
        search_options = [
            {"type": "other", "value": "abc", "search_column": "dept"}
        ]

        search = MultiColumnDatabaseSearch('mc_search', 'order_id')

        with pytest.raises(ValueError):
            search.build_search_values(data, search_options)

    def test_build_field_search(self):
        data = {
            "abc": "xyz"
        }
        search_options = [
            {"type": "field", "source_name": "abc", "search_column": "dept"}
        ]

        search = MultiColumnDatabaseSearch('mc_search', 'order_id')
        search_values = search.build_search_values(data, search_options)

        assert search_values == {'dept': 'xyz'}

    def test_build_split_field_search(self):
        data = {
            "abc": "Smith, Bob"
        }
        search_options = [
            {
                "type": "split",
                "source_name": "abc",
                "split_char": ",",
                "matches":  [
                    {
                        "field_index": 1,
                        "search_column": "first_name"
                    },
                    {
                        "field_index": 0,
                        "search_column": "last_name"
                    }
                ]

            }
        ]

        search = MultiColumnDatabaseSearch('mc_search', 'order_id')
        search_values = search.build_search_values(data, search_options)

        assert search_values == {'first_name': 'Bob', 'last_name': 'Smith'}

    def test_build_split_field_search_with_invalid_matches(self):
        data = {
            "abc": "Smith, Bob"
        }
        search_options = [
            {
                "type": "split",
                "source_name": "abc",
                "split_char": ",",
                "matches":  [
                    {
                        "field_index": 1,
                        "search_column": "first_name"
                    },
                    {
                        "field_index": 0,
                        "search_column": "last_name"
                    },
                    {
                        "field_index": 2,
                        "search_column": "other_name"
                    }
                ]

            }
        ]

        search = MultiColumnDatabaseSearch('mc_search', 'order_id')
        search_values = search.build_search_values(data, search_options)

        assert search_values == {'first_name': 'Bob', 'last_name': 'Smith'}


