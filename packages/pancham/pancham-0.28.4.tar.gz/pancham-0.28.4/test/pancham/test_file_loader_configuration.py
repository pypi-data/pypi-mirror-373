import json

from pancham.file_loader_configuration import FileLoaderConfiguration

class TestFileLoaderConfiguration:

    def test_hashes(self):
        config = FileLoaderConfiguration(
            sheet='a',
            file_path='b',
            file_type='c',
            key='d',
            query=None
        )

        assert hash(config) == hash(('d', 'c', 'a', 'b', None))


    def test_hashes_with_list(self):
        config = FileLoaderConfiguration(
            sheet='a',
            file_path=['x', 'y'],
            file_type='c',
            key='d',
            query=None
        )

        paths = json.dumps(['x', 'y'])
        assert hash(config) == hash(('d', 'c', 'a', paths, None))