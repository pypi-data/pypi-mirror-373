import os
import pytest

from pancham.data_frame_configuration import DataFrameConfiguration
from pancham.file_loader import ExcelFileLoader, YamlFileLoader, JsonFileLoader


class TestExcelFileLoader():

    def test_load_excel_file(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/orders.xlsx"

        loader = ExcelFileLoader()
        data = loader.read_file(filename, sheet = 'Sheet1')

        assert len(data) == 10

    def test_load_without_sheet(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/orders.xlsx"

        loader = ExcelFileLoader()
        with pytest.raises(ValueError):
            loader.read_file(filename)

    def test_load_missing_excel_file(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../not_there.xlsx"

        loader = ExcelFileLoader()

        with pytest.raises(FileNotFoundError):
            loader.read_file(filename, sheet = 'Sheet1')

    def test_yaml_file_loader(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/orders.yaml"

        loader = YamlFileLoader()
        data = loader.read_file(filename, key = 'orders')

        assert len(data) == 2
        assert data.iloc[0]['name'] == 'A'

    def test_read_from_configuration(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/orders.xlsx"
        configuration = DataFrameConfiguration(filename, 'xlsx', 'a', sheet='Sheet1')

        loader = ExcelFileLoader()
        data = next(loader.read_file_from_configuration(configuration))

        assert len(data) == 10

    def test_read_from_yaml_configuration(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/orders.yaml"
        configuration = DataFrameConfiguration(filename, 'yaml', 'a', key='orders')

        loader = YamlFileLoader()
        data = next(loader.read_file_from_configuration(configuration))

        assert len(data) == 2

    def test_read_from_json_configuration(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/orders.json"
        configuration = DataFrameConfiguration(filename, 'json', 'a')

        loader = JsonFileLoader()
        iter = loader.read_file_from_configuration(configuration)
        data = list(iter)[0]

        assert len(data) == 6

    def test_read_from_json_configuration_and_key(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/orders.json"
        configuration = DataFrameConfiguration(filename, 'json', 'a', key='orders')

        loader = JsonFileLoader()
        data = next(loader.read_file_from_configuration(configuration))

        assert len(data) == 6
