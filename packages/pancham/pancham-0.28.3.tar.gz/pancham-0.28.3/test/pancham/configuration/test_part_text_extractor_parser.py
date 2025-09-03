import pytest

from configuration.part_text_extractor_parser import PartTextExtractorParser


class TestPartTextExtractorParser:

    def test_can_parse(self):
        field = {
            'name': 'a',
            'func': {
                'split_extract': {}
            }
        }

        parser = PartTextExtractorParser()
        assert parser.can_parse_field(field)


    def test_parse_valid_name(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 0
                }
            }
        }

        input = {
            'a': 'Really Big Company Ltd'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == 'Really'

    def test_parse_multiple_parts_valid_name(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 1,
                    'split_limit': 1
                }
            }
        }

        input = {
            'a': 'Really Big Company Ltd'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == 'Big Company Ltd'

    def test_parse_multiple_parts_valid_name_and_remove(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 1,
                    'split_limit': 1,
                    'remove': ['Ltd']
                }
            }
        }

        input = {
            'a': 'Really Big Company Ltd'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == 'Big Company'

    def test_parse_and_get_none(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 10,
                    'remove': ['Ltd'],
                    'error_value': None
                }
            }
        }

        input = {
            'a': 'Really Big Company Ltd'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == None

    def test_parse_and_get_none_with_minimum_parts(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 1,
                    'minimum_expected_parts': 8,
                    'error_value': None
                }
            }
        }

        input = {
            'a': 'Really Big Company Ltd'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == None

    def test_parse_and_get_none_with_minimum_parts_and_input_return(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 1,
                    'minimum_expected_parts': 8,
                    'error_value': 'input'
                }
            }
        }

        input = {
            'a': 'Really Big Company Ltd'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == 'Really Big Company Ltd'

    def test_parse_and_get_none_with_fixed_return(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 1,
                    'error_value': 'input',
                    'length_return_values': [
                        {
                            'length': 3,
                            'return_type': 'input'
                        }
                    ]
                }
            }
        }

        input = {
            'a': 'Really Big Company'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == 'Really Big Company'

    def test_parse_and_get_none_with_fixed_return_index(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 1,
                    'error_value': 'input',
                    'length_return_values': [
                        {
                            'length': 3,
                            'return_type': 'index',
                            'value': 2
                        }
                    ]
                }
            }
        }

        input = {
            'a': 'Really Big Company'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == 'Company'

    def test_parse_and_get_none_with_fixed_return_set(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'splitter': ' ',
                    'return_index': 1,
                    'error_value': 'input',
                    'length_return_values': [
                        {
                            'length': 3,
                            'value': 'Invalid'
                        }
                    ]
                }
            }
        }

        input = {
            'a': 'Really Big Company'
        }

        parser = PartTextExtractorParser()

        data_field = parser.parse_field(field)
        assert data_field.name == 'Startname'
        assert data_field.func(input) == 'Invalid'


    def test_parse_without_splitter(self):
        field = {
            'name': 'Startname',
            'source_name': 'a',
            'func': {
                'split_extract': {
                    'return_index': 1,
                    'minimum_expected_parts': 8,
                    'error_value': None
                }
            }
        }

        input = {
            'a': 'Really Big Company Ltd'
        }

        with pytest.raises(ValueError):
            parser = PartTextExtractorParser()
            data_field = parser.parse_field(field)

            data_field.func(input)

