import pandas as pd
import numpy as np
from configuration.fillnan_field_parser import FillNanFieldParser


class TestFillNanFieldParser:


    def test_parse_field(self):
        parser = FillNanFieldParser()
        field = {
            'name': 'a',
            'func': {
                'fill_nan': {}
            }
        }

        assert parser.can_parse_field(field)

    def test_explode_field(self):
        parser = FillNanFieldParser()
        field = {
            'name': 'a',
            'field_type': 'str',
            'func': {
                'fill_nan': {
                    'source_name': 'b',
                    'replace_value': 0
                }
            }
        }

        dfield = parser.parse_field(field)

        data= pd.DataFrame({
            'b': [1, 2, np.nan, 4]
        })

        out = dfield.df_func(data)

        assert len(out) == 4
        assert out['b'].iloc[0] == 1
        assert out['b'].iloc[1] == 2
        assert out['b'].iloc[2] == 0
        assert out['b'].iloc[3] == 4
