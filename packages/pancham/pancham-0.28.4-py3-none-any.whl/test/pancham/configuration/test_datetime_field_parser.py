import datetime
import pandas as pd
from pancham.configuration.datetime_field_parser import DateTimeFieldParser

def pytest_generate_tests(metafunc):
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )

class TestDatetimeFieldParser:

    params = {
        "test_can_parse_datetime_field": [
            dict(field=dict(name= 'a', func = dict(datetime = dict())), expected=True),
            dict(field=dict(name= 'a', func = dict()), expected=False),
        ],
        "test_parse": [
            dict(name = 'a', source_name = 'b', func = dict(datetime = dict()), nullable = True, input = "01/02/2024"),
            dict(name='a', source_name='b', func = dict(datetime = dict(format = '%m/%d/%Y')), nullable=False, input = "02/01/2024"),
        ]
    }

    def test_can_parse_datetime_field(self, field, expected):
        parser = DateTimeFieldParser()

        assert parser.can_parse_field(field) == expected

    def test_parse(self, name, source_name, func, nullable, input):
        field = {
            'name': name,
            'source_name': source_name,
            'nullable': nullable,
            'func': func
        }

        input_data = {
            source_name: input
        }

        parser = DateTimeFieldParser()
        data_field = parser.parse_field(field)

        assert data_field.name == name
        assert data_field.nullable == nullable

        assert data_field.func(input_data).year == 2024
        assert data_field.func(input_data).month == 2
        assert data_field.func(input_data).day == 1
