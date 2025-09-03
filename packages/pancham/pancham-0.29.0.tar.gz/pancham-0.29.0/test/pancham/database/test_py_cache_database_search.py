from sqlalchemy import MetaData, Table, Column, String, Integer, UniqueConstraint
import pandas as pd

from pancham.database.database_engine import get_db_engine, initialize_db_engine
from pancham.database.py_database_cache_search import PyDatabaseCacheSearch
from pancham.reporter import PrintReporter
from pancham_configuration import PanchamConfiguration

class MockConfig(PanchamConfiguration):

    @property
    def database_connection(self) -> str:
        return "sqlite:///:memory:"

class TestPyCachingDatabaseSearch:

    def test_engine_write_df(self):
        initialize_db_engine(MockConfig(), PrintReporter())

        meta = MetaData()
        Table('order0', meta, Column("email", String), Column("order_id", String))

        meta.create_all(get_db_engine().engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com'], 'order_id': ['1', '2']})

        get_db_engine().write_df(data, 'order0')

        search = PyDatabaseCacheSearch('order0', 'email', 'order_id')

        assert search.get_mapped_id('b@example.com') == '2'
        assert search.get_mapped_id('b@example.com') == '2' # Use cache
        assert search.get_mapped_id('c@example.com') is None
