from sqlalchemy import MetaData, Table, Column, String, Integer
import pandas as pd

from pancham.database.database_engine import get_db_engine, initialize_db_engine
from pancham.reporter import PrintReporter
from pancham.database.populating_database_search import PopulatingDatabaseSearch
from pancham_configuration import PanchamConfiguration

class MockConfig(PanchamConfiguration):

    @property
    def database_connection(self) -> str:
        return "sqlite:///:memory:"

class TestPopulatingDatabaseSearch:

    def test_engine_write_df(self):
        initialize_db_engine(MockConfig(), PrintReporter())
        table_name = 'orderpop0'

        meta = MetaData()
        Table(table_name, meta, Column("order_id", Integer, primary_key=True, autoincrement=True), Column("email", String))

        meta.create_all(get_db_engine().engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com']})

        get_db_engine().write_df(data, table_name)

        search = PopulatingDatabaseSearch(table_name, 'email', 'order_id')

        assert search.get_mapped_id('b@example.com') == 2
        assert search.get_mapped_id('c@example.com') == 3
