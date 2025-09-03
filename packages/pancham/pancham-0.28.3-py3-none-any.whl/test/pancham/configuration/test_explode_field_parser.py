import pandas as pd

from configuration.explode_field_parser import ExplodeFieldParser

class TestExplodeFieldParser:


    def test_parse_field(self):
        parser = ExplodeFieldParser()
        field = {
            'name': 'a',
            'func': {
                'explode': {}
            }
        }

        assert parser.can_parse_field(field)

    def test_explode_field(self):
        parser = ExplodeFieldParser()
        field = {
            'name': 'a',
            'field_type': 'str',
            'func': {
                'explode': {
                    'source_name': 'b',
                }
            }
        }

        dfield = parser.parse_field(field)

        data= pd.DataFrame({
            'b': [['a', 'b'], ['c', 'd']]
        })

        out = dfield.df_func(data)

        assert len(out) == 4

    def test_explode_field_with_empty_values(self):
        parser = ExplodeFieldParser()
        field = {
            'name': 'a',
            'field_type': 'str',
            'func': {
                'explode': {
                    'drop_nulls': True,
                    'source_name': 'b',
                }
            }
        }

        dfield = parser.parse_field(field)

        data= pd.DataFrame({
            'b': [['a', 'b'], ['c', None]]
        })

        out = dfield.df_func(data)

        assert len(out) == 3
