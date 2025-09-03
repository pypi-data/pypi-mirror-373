from pancham.tool.str_tools import remove_and_split


class TestStrTools:

    def test_non_split(self):
        output = remove_and_split('a', ':')

        assert output[0] == 'a'

    def test_split(self):
        output = remove_and_split('a:b', ':')

        assert output[0] == 'a'
        assert output[1] == 'b'

    def test_split_pattern(self):
        output = remove_and_split('a9:b', ':', '\d+')

        assert output[0] == 'a'
        assert output[1] == 'b'

    def test_split_pattern_value(self):
        output = remove_and_split('a:9:b', ':', '\d+')

        assert output[0] == 'a'
        assert output[1] == 'b'

    def test_split_number(self):
        output = remove_and_split('a:9:b', ':')

        assert output[0] == 'a'
        assert output[1] == '9'
        assert output[2] == 'b'
