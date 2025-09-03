from pancham_configuration import OrderedPanchamConfiguration
import os


class TestOrderedPanchamConfiguration():

    filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/config.yaml"

    def test_get_db_connection_from_file(self):
        config = OrderedPanchamConfiguration(self.filename)

        assert config.database_connection == 'sqlite:////test.db'

    def test_get_db_connection_from_env(self):
        config = OrderedPanchamConfiguration(self.filename)
        os.environ['PANCHAM_DATABASE_CONNECTION'] = 'sqlite:////other.db'

        assert config.database_connection == 'sqlite:////other.db'

    def test_get_db_connection_from_none(self):
        config = OrderedPanchamConfiguration(None)
        del os.environ['PANCHAM_DATABASE_CONNECTION']

        assert config.database_connection is None

    def test_get_test_files(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/../example/config_with_test.yaml"
        config = OrderedPanchamConfiguration(filename)

        assert config.test_files == ['example.yml']
