import csv

import numpy as np
import pandas as pd

from pancham.integration.salesforce_output import pd_to_sf_dict

def read_file(filename: str):
    content = []
    with open(filename, 'r') as file:
        reader = csv.reader(file, delimiter=',')

        for row in reader:
            content.append(row)

    return content

class TestPdToSf:

    def test_transform_basic(self):
        data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

        output = pd_to_sf_dict(data)

        assert output is not None

        content = read_file(output)

        assert content[1][0] == '1'
        assert content[1][1] == '4'


    def test_transform_boolean(self):
        data = pd.DataFrame({'a': [True, False, True], 'b': [4, 5, 6]})

        output = pd_to_sf_dict(data, bool_cols=['a'])

        assert output is not None

        content = read_file(output)
        assert content[1][0] == 'true'
        assert content[1][1] == '4'
        assert content[2][0] == 'false'

    def test_transform_nan(self):
        data = pd.DataFrame({'a': [1, np.nan, 3], 'b': [4, 5, 6]})

        output = pd_to_sf_dict(data, int_cols=['a', 'b'])
        assert output is not None

        content = read_file(output)
        assert content[1][0] == '1'
        assert content[1][1] == '4'
        assert content[2][0] == ''

    def test_transform_float(self):
        data = pd.DataFrame({'a': [1, 2.3, 3.2], 'b': [4, 5, 6]})

        output = pd_to_sf_dict(data)

        assert output is not None

        content = read_file(output)
        assert content[1][0] == '1.0'
        assert content[1][1] == '4'
        assert content[2][0] == '2.3'