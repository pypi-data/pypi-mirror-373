import pytest

from configuration.match_field_parser import MatchFieldParser

def pytest_generate_tests(metafunc):
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )

class TestMatchFieldParser:


    params = {
        "test_can_parse_eq_field": [
            dict(field=dict(name= 'a', func = dict(eq = dict(source_name = 'a', match='b'))), expected=True),
            dict(field=dict(name='a', func = dict()), expected=False)
        ],
        "test_parse": [
            dict(name='a', func=dict(eq=dict(source_name='a', match='b'))),
        ],
        "test_no_source_name": [
            dict(func=dict(eq=dict(match='b'))),
        ]
    }

    def test_can_parse_eq_field(self, field, expected):
        parser = MatchFieldParser()

        assert parser.can_parse_field(field) == expected

    def test_parse(self, name, func):
        field = {
            'name': name,
            'func': func
        }

        parser = MatchFieldParser()
        data_field = parser.parse_field(field)

        assert data_field.name == name
        assert data_field.source_name == None
        assert data_field.nullable == False

    def test_no_source_name(self, func):
        field = {
            'name': 'a',
            'func': func
        }

        with pytest.raises(ValueError):
            parser = MatchFieldParser()
            parser.parse_field(field)
