from pancham.data_frame_field import DataFrameField
from pancham.data_frame_configuration import DataFrameConfiguration


class TestDataFrameConfiguration:

    def test_add_field_with_separate_values(self):
        config = self.__build()
        config.add_field('b', 'c', int, False)

        assert config.file_path == 'a'
        assert config.file_type == 'xlsx'
        assert len(config.fields) == 1

        field = config.fields[0]
        assert field.name == 'b'
        assert field.source_name == 'c'
        assert field.field_type == int
        assert field.nullable == False

    def test_add_field_with_field_value(self):
        data_frame_field = DataFrameField('b', 'c', int, False)
        config = self.__build()
        config.add_field(data_frame_field=data_frame_field)

        assert config.file_path == 'a'
        assert config.file_type == 'xlsx'
        assert len(config.fields) == 1

        field = config.fields[0]
        assert field.name == 'b'
        assert field.source_name == 'c'
        assert field.field_type == int
        assert field.nullable == False

    def test_add_dynamic_field(self):
        config = self.__build()
        config.add_dynamic_field('b', func = lambda row: row['c'] + 1)

        assert len(config.fields) == 1
        assert len(config.dynamic_fields) == 1
        assert len(config.renames) == 0

    def __build(self) -> DataFrameConfiguration:
        return DataFrameConfiguration('a', 'xlsx', 'a')
