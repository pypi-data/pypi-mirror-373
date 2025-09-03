from sqlalchemy import MetaData, Table, Column, String, Integer, UniqueConstraint
import pandas as pd
import os

from pancham.database.database_search_manager import get_database_search
from pancham.database.database_engine import get_db_engine, initialize_db_engine
from pancham.reporter import PrintReporter
from pancham.database.caching_database_search import CachingDatabaseSearch, SQLFileCachingDatabaseSearch
from pancham_configuration import PanchamConfiguration

class MockConfig(PanchamConfiguration):

    @property
    def database_connection(self) -> str:
        return "sqlite:///:memory:"

class TestCachingDatabaseSearch:

    def test_engine_write_df(self):
        initialize_db_engine(MockConfig(), PrintReporter())

        meta = MetaData()
        Table('order0', meta, Column("email", String), Column("order_id", String))

        meta.create_all(get_db_engine().engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com'], 'order_id': ['1', '2']})

        get_db_engine().write_df(data, 'order0')

        search = CachingDatabaseSearch('order0', 'email', 'order_id')

        assert search.get_mapped_id('b@example.com') == '2'
        assert search.get_mapped_id('c@example.com') is None

    def test_cast_engine_write_df(self):
        initialize_db_engine(MockConfig(), PrintReporter())

        meta = MetaData()
        Table('order2', meta, Column("email", String), Column("order_id", String))

        meta.create_all(get_db_engine().engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com'], 'order_id': ['1', '2']})

        get_db_engine().write_df(data, 'order2')

        search = get_database_search('order2', 'email', 'order_id', None,'str', 'int')

        assert search.get_mapped_id('b@example.com') == 2
        assert search.get_mapped_id('c@example.com') is None

    def test_cast_filter_engine_write_df(self):
        initialize_db_engine(MockConfig(), PrintReporter())

        meta = MetaData()
        Table('order3', meta, Column("email", String), Column("order_id", String), Column("active", String))

        meta.create_all(get_db_engine().engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com'], 'order_id': ['1', '2'], 'active':['N', 'Y']})

        get_db_engine().write_df(data, 'order3')

        search = get_database_search('order3', 'email', 'order_id', {'active': 'Y'},'str', 'int')

        assert search.get_mapped_id('b@example.com') == 2
        assert search.get_mapped_id('c@example.com') is None
        assert search.get_mapped_id('a@example.com') is None

    def test_find_data_with_sqlite_and_filter(self):
        table_name = 'customer9'
        type_name = f'{table_name}_type'

        config = MockConfig()
        initialize_db_engine(config, PrintReporter())
        db_engine = get_db_engine()

        meta = MetaData()
        Table(table_name, meta, Column("email", String), Column("customer_name", String), Column("type",Integer))
        Table(type_name, meta, Column("type_id", Integer), Column("type_name", String), UniqueConstraint('type_id', name='type_unique_constraint'))
        meta.create_all(db_engine.engine)

        type_data = pd.DataFrame({'type_id': [1, 2], 'type_name': ['A', 'B']})
        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com'], 'type': [1, 2], 'customer_name': ['A', 'B']})

        db_engine.write_df(type_data, type_name)
        db_engine.write_df(data, table_name)

        id_search = SQLFileCachingDatabaseSearch(f'{os.path.dirname(os.path.realpath(__file__))}/../../example/customer_type_load.sql')
        type_id = id_search.get_mapped_id('B')

        assert type_id == 2
