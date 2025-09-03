from configuration.text_field_parser import TextFieldParser

def pytest_generate_tests(metafunc):
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )


class TestTextFieldParser:

    params = {
        "test_can_parse_text_field": [
            dict(field=dict(name='a', source_name='b', field_type='datetime'), expected=False),
            dict(field=dict(name='a', source_name='b', field_type='str'), expected=True),
            dict(field=dict(source_name='b', field_type='str'), expected=False),
            dict(field=dict(name='a', field_type='str'), expected=False),
        ],
        "test_parse": [
            dict(name='a', source_name='b', nullable=True),
            dict(name='a', source_name='b', nullable=False),
        ]
    }

    def test_can_parse_text_field(self, field, expected):
        parser = TextFieldParser()

        assert parser.can_parse_field(field) == expected

    def test_parse(self, name, source_name, nullable):
        field = {
            'name': name,
            'source_name': source_name,
            'nullable': nullable
        }

        parser = TextFieldParser()
        data_field = parser.parse_field(field)

        assert data_field.name == name
        assert data_field.source_name == source_name
        assert data_field.nullable == nullable
