import datetime
import os

import pandas as pd
import pytest
from pandas._testing import assert_frame_equal
from pandera.errors import SchemaError

from pancham.data_frame_configuration import DataFrameConfiguration, MergeConfiguration
from pancham.data_frame_loader import DataFrameLoader, DataFrameOutput
from pancham.file_loader import ExcelFileLoader
from pancham.reporter import PrintReporter
from pancham_configuration import StaticPanchamConfiguration


class TestDataFrameLoader:

    filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/orders.xlsx"

    def test_load_example_data(self):
        loader = DataFrameLoader({'xlsx': ExcelFileLoader()}, PrintReporter())
        configuration = DataFrameConfiguration(self.filename, 'xlsx', 'a', sheet='Sheet1')
        configuration.add_field('Order', 'Order Id', int)
        configuration.add_field('Date', 'Rec Date', datetime.datetime)
        configuration.add_dynamic_field('Sent', field_type=bool, func=lambda row: row['Disp.'] == 'X')

        data = next(loader.load(configuration)).processed

        assert len(data) == 10
        assert data.loc[0, 'Order'] == 1
        assert data.loc[0, 'Date'] == datetime.datetime(2024, 12, 22)
        assert data.loc[0, 'Sent'] == True

        assert data.loc[9, 'Order'] == 10
        assert data.loc[9, 'Date'] == datetime.datetime(2024, 12, 31)
        assert data.loc[9, 'Sent'] == False

    def test_load_example_data_with_static_field(self):
        loader = DataFrameLoader({'xlsx': ExcelFileLoader()}, PrintReporter())
        configuration = DataFrameConfiguration(self.filename, 'xlsx', 'a', sheet='Sheet1')
        configuration.add_field('Order', 'Order Id', int)
        configuration.add_dynamic_field('Sent', field_type=bool, func=lambda row: row['Disp.'] == 'X')
        configuration.add_dynamic_field('Static', field_type=str, func=lambda row: 'abc')

        data = next(loader.load(configuration)).processed

        assert len(data) == 10
        assert data.loc[0, 'Order'] == 1
        assert data.loc[0, 'Sent'] == True
        assert data.loc[0, 'Static'] == 'abc'

        assert data.loc[9, 'Order'] == 10
        assert data.loc[9, 'Sent'] == False

    def test_load_example_data_with_schema_validation(self):
        loader = DataFrameLoader({'xlsx': ExcelFileLoader()}, PrintReporter())
        configuration = DataFrameConfiguration(self.filename, 'xlsx', 'a', sheet='Sheet1')
        configuration.add_field('Order', 'Order Id', int)
        configuration.add_field('Date', 'Rec Date', int)

        with pytest.raises(SchemaError):
            next(loader.load(configuration))

    def test_load_example_data_with_schema_validation_and_validation_disabled(self):
        pancham_configuration = StaticPanchamConfiguration('', False, '', True)
        loader = DataFrameLoader({'xlsx': ExcelFileLoader()}, PrintReporter(), pancham_configuration=pancham_configuration)
        configuration = DataFrameConfiguration(self.filename, 'xlsx', 'a', sheet='Sheet1')
        configuration.add_field('Order', 'Order Id', int)
        configuration.add_field('Date', 'Rec Date', int)

        data = next(loader.load(configuration)).processed

        assert len(data) == 10
        assert data.loc[0, 'Order'] == 1

class TestDataFrameOutput:

    def test_get_required_without_merge(self):
        frame1 = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        frame2 = pd.DataFrame({'c': [1, 2, 3]})

        output = DataFrameOutput(frame1, frame2)

        assert_frame_equal(frame2, output.get_required_dataframe(None))

    def test_get_required_with_processed_merge(self):
        merge = MergeConfiguration('processed')
        frame1 = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        frame2 = pd.DataFrame({'c': [1, 2, 3]})

        output = DataFrameOutput(frame1, frame2)

        assert_frame_equal(frame2, output.get_required_dataframe(merge))

    def test_get_required_with_source_merge(self):
        merge = MergeConfiguration('source')
        frame1 = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        frame2 = pd.DataFrame({'c': [1, 2, 3]})

        output = DataFrameOutput(frame1, frame2)

        assert_frame_equal(frame1, output.get_required_dataframe(merge))

    def test_get_required_with_merge(self):
        merge = MergeConfiguration('merged', 'a', 'c')
        frame1 = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        frame2 = pd.DataFrame({'c': [1, 2, 3]})

        output = DataFrameOutput(frame1, frame2).get_required_dataframe(merge)

        assert output.iloc[0]['a'] == 1
        assert output.iloc[0]['b'] == 'x'
        assert output.iloc[0]['c'] == 1
