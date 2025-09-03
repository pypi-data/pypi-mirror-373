from pancham.data_frame_field import DataFrameField

class TestDataFrameField():
    def test_is_not_dynamic(self):
        field = DataFrameField('a', 'b', str)

        assert field.is_dynamic() == False

    def test_is_dynamic(self):
        field = DataFrameField('a', 'b', str, func = lambda x: x)

        assert field.is_dynamic() == True

    def test_str(self):
        field = DataFrameField('a', 'b', str)

        str_field = str(field)
        expected = "Name: a, Source Name: b, Type: <class 'str'>, Nullable: True"

        assert str_field == expected
