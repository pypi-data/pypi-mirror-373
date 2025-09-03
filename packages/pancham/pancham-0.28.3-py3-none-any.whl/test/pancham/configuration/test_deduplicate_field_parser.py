import datetime

import pandas as pd

from configuration.deduplicate_field_parser import DeduplicateFieldParser


class TestExplodeFieldParser:


    def test_parse_field(self):
        parser = DeduplicateFieldParser()
        field = {
            'name': 'a',
            'func': {
                'deduplicate': {}
            }
        }

        assert parser.can_parse_field(field)

    def test_deduplicate_field(self):
        parser = DeduplicateFieldParser()
        field = {
            'name': 'a',
            'field_type': 'str',
            'func': {
                'deduplicate': {
                    'source_name': 'b',
                }
            }
        }

        dfield = parser.parse_field(field)

        data= pd.DataFrame({
            'b': ['a', 'c', 'd', 'd'],
            'c': [1, 2, 3, 4]
        })

        out = dfield.df_func(data)

        assert len(out) == 3

    def test_deduplicate_and_sort(self):
        parser = DeduplicateFieldParser()
        field = {
            'name': 'a',
            'field_type': 'str',
            'func': {
                'deduplicate': {
                    'source_name': 'b',
                    'sort_by': ['c']

                }
            }
        }

        dfield = parser.parse_field(field)

        data= pd.DataFrame({
            'b': ['a', 'c', 'd', 'd', 'd'],
            'c': [1, 2, 3, 4, 1]
        })

        out = dfield.df_func(data)

        assert len(out) == 3
        assert out['c'].iloc[2] == 1


    def test_deduplicate_and_sort_date(self):
        parser = DeduplicateFieldParser()
        field = {
            'name': 'a',
            'field_type': 'str',
            'func': {
                'deduplicate': {
                    'source_name': 'b',
                    'sort_by': ['c']

                }
            }
        }

        dfield = parser.parse_field(field)

        data= pd.DataFrame({
            'b': ['a', 'c', 'd', 'd', 'd'],
            'c': [
                datetime.date(2025, 1,1),
                datetime.date(2025, 1,1),
                datetime.date(2024, 1, 1),
                datetime.date(2025, 1, 1),
                datetime.date(2000, 1, 1)]
        })

        out = dfield.df_func(data)

        assert len(out) == 3
        assert out['c'].iloc[2] == datetime.date(2000, 1, 1)

    def test_deduplicate_and_sort_desc(self):
        parser = DeduplicateFieldParser()
        field = {
            'name': 'a',
            'field_type': 'str',
            'func': {
                'deduplicate': {
                    'source_name': 'b',
                    'sort_by': ['c'],
                    'ascending': False,
                }
            }
        }

        dfield = parser.parse_field(field)

        data= pd.DataFrame({
            'b': ['a', 'c', 'd', 'd', 'd'],
            'c': [1, 2, 3, 4, 1]
        })

        out = dfield.df_func(data)

        assert len(out) == 3
        assert out['c'].iloc[0] == 4

    def test_deduplicate_and_sort_date_desc(self):
        parser = DeduplicateFieldParser()
        field = {
            'name': 'a',
            'field_type': 'str',
            'func': {
                'deduplicate': {
                    'source_name': 'b',
                    'sort_by': ['c'],
                    'ascending': False
                }
            }
        }

        dfield = parser.parse_field(field)

        data= pd.DataFrame({
            'b': ['a', 'c', 'd', 'd', 'd'],
            'c': [
                datetime.date(2025, 1,1),
                datetime.date(2025, 1,1),
                datetime.date(2024, 1, 1),
                datetime.date(2025, 1, 1),
                datetime.date(2000, 1, 1)]
        })

        out = dfield.df_func(data)

        assert len(out) == 3
        assert out['c'].iloc[2] == datetime.date(2025, 1, 1)
